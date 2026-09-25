from db.model.database import db_config
from src.tool.ecpay_tool import generate_check_mac_value, parse_notify_form_body, verify_notify_check_mac_value


class TestGenerateCheckMacValue:
    def test_deterministic(self):
        params = {
            "MerchantID": "2000132",
            "MerchantTradeNo": "abc123",
            "TotalAmount": "100",
        }
        mac1 = generate_check_mac_value(params, hash_key="HASHKEY", hash_iv="HASHIV")
        mac2 = generate_check_mac_value(params, hash_key="HASHKEY", hash_iv="HASHIV")

        assert mac1 == mac2
        assert len(mac1) == 64
        assert mac1 == mac1.upper()

    def test_tamper_changes_mac_value(self):
        params = {
            "MerchantID": "2000132",
            "MerchantTradeNo": "abc123",
            "TotalAmount": "100",
        }
        original = generate_check_mac_value(params, hash_key="HASHKEY", hash_iv="HASHIV")

        tampered = dict(params)
        tampered["TotalAmount"] = "999"
        changed = generate_check_mac_value(tampered, hash_key="HASHKEY", hash_iv="HASHIV")

        assert original != changed

    def test_existing_check_mac_value_field_is_ignored(self):
        params = {
            "MerchantID": "2000132",
            "TotalAmount": "100",
        }
        without_mac = generate_check_mac_value(params, hash_key="HASHKEY", hash_iv="HASHIV")

        with_mac = dict(params)
        with_mac["CheckMacValue"] = "SOME_OLD_VALUE"
        with_mac_result = generate_check_mac_value(with_mac, hash_key="HASHKEY", hash_iv="HASHIV")

        assert without_mac == with_mac_result

    def test_special_characters_are_restored_not_percent_encoded(self):
        """
        綠界規範要求 -_.!*()（.NET UrlEncode 的保留字元）在雜湊前要還原，
        確保這些字元不會被當成一般符號直接進行 percent-encode。
        """
        params = {"TradeDesc": "test-value_ok.done!go*now(1)"}
        # 主要驗證函式不會丟出例外，且雜湊值為固定長度的十六進位大寫字串
        mac_value = generate_check_mac_value(params, hash_key="HASHKEY", hash_iv="HASHIV")
        assert len(mac_value) == 64
        assert all(c in "0123456789ABCDEF" for c in mac_value)


class TestParseNotifyFormBody:
    def test_recovers_unencoded_utf8_chinese_value(self):
        """
        迴歸測試：綠界回呼的中文欄位（如 RtnMsg）常常不做 percent-encoding，
        直接把原始 UTF-8 位元組塞進 application/x-www-form-urlencoded body。
        FastAPI/Starlette 的 request.form() 會用 Latin-1 逐位元組解析，
        導致中文變亂碼、CheckMacValue 驗證失敗（曾實際在串接測試中發生過）。
        parse_notify_form_body 要能正確還原這種未編碼的中文欄位。
        """
        body = "RtnMsg=交易成功&RtnCode=1&MerchantTradeNo=abc123".encode("utf-8")

        parsed = parse_notify_form_body(body)

        assert parsed["RtnMsg"] == "交易成功"
        assert parsed["RtnCode"] == "1"
        assert parsed["MerchantTradeNo"] == "abc123"

    def test_parsed_body_passes_check_mac_value_verification(self, monkeypatch):
        """
        端對端驗證：用 parse_notify_form_body 解析出來的參數，
        重新計算的 CheckMacValue 要跟綠界原本送來的一致（不受中文亂碼影響）。
        """
        hash_key, hash_iv = "HASHKEY", "HASHIV"
        monkeypatch.setitem(db_config["ECPAY"], "hash_key", hash_key)
        monkeypatch.setitem(db_config["ECPAY"], "hash_iv", hash_iv)

        params = {"RtnMsg": "交易成功", "RtnCode": "1", "MerchantTradeNo": "abc123"}
        mac_value = generate_check_mac_value(params, hash_key=hash_key, hash_iv=hash_iv)
        body = f"RtnMsg=交易成功&RtnCode=1&MerchantTradeNo=abc123&CheckMacValue={mac_value}".encode("utf-8")

        parsed = parse_notify_form_body(body)

        assert verify_notify_check_mac_value(parsed) is True
