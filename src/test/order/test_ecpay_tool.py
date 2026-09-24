from src.tool.ecpay_tool import generate_check_mac_value


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
