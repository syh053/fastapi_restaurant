import hashlib
from datetime import datetime
from urllib.parse import quote_plus, parse_qsl

from db.model import Order, OrderItem
from db.model.database import db_config


def _dotnet_url_encode(raw: str) -> str:
    """
    比照 .NET HttpUtility.UrlEncode 的編碼規則（綠界文件要求），
    quote_plus 後轉小寫，再把特定字元還原成未編碼狀態。
    """
    encoded = quote_plus(raw).lower()
    replacements = (
        ("%2d", "-"),
        ("%5f", "_"),
        ("%2e", "."),
        ("%21", "!"),
        ("%2a", "*"),
        ("%28", "("),
        ("%29", ")"),
    )
    for old, new in replacements:
        encoded = encoded.replace(old, new)
    return encoded


def generate_check_mac_value(params: dict, hash_key: str, hash_iv: str) -> str:
    """
    依綠界規範計算 CheckMacValue：
    參數依 key A-Z 排序 -> 前後補上 HashKey/HashIV -> URL encode -> 轉小寫 -> SHA256 -> 轉大寫
    """
    filtered = {k: v for k, v in params.items() if k != "CheckMacValue" and v is not None}
    sorted_items = sorted(filtered.items(), key=lambda item: item[0])
    query_string = "&".join(f"{key}={value}" for key, value in sorted_items)
    raw = f"HashKey={hash_key}&{query_string}&HashIV={hash_iv}"
    encoded = _dotnet_url_encode(raw)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_notify_check_mac_value(form_data: dict) -> bool:
    received_mac_value = form_data.get("CheckMacValue")
    if not received_mac_value:
        return False

    calculated = generate_check_mac_value(
        form_data,
        hash_key=db_config["ECPAY"]["hash_key"],
        hash_iv=db_config["ECPAY"]["hash_iv"],
    )
    return calculated == received_mac_value


def build_aio_checkout_params(order: Order, items: list[OrderItem]) -> dict:
    item_name = "#".join(f"{item.name} x{item.quantity}" for item in items)

    params = {
        "MerchantID": db_config["ECPAY"]["merchant_id"],
        "MerchantTradeNo": order.merchant_trade_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": str(order.total_amount),
        "TradeDesc": "餐廳訂單結帳",
        "ItemName": item_name,
        "ReturnURL": db_config["ECPAY"]["return_url"],
        "ClientBackURL": db_config["ECPAY"]["client_back_url"],
        "ChoosePayment": "Credit",
        "EncryptType": "1",
    }
    params["CheckMacValue"] = generate_check_mac_value(
        params,
        hash_key=db_config["ECPAY"]["hash_key"],
        hash_iv=db_config["ECPAY"]["hash_iv"],
    )
    return params


def get_action_url() -> str:
    return db_config["ECPAY"]["action_url"]


def parse_notify_form_body(body: bytes) -> dict:
    """
    解析綠界 Server 端回呼的 application/x-www-form-urlencoded body。

    綠界的中文欄位（如 RtnMsg）常常沒有做 percent-encoding，直接塞原始 UTF-8 位元組，
    FastAPI/Starlette 的 request.form() 會用 Latin-1 逐位元組解析而產生亂碼，
    導致 CheckMacValue 驗證失敗。這裡改成先把整段 body 當 UTF-8 文字解碼，再用
    parse_qsl 拆解，才能正確還原中文欄位內容。
    """
    return dict(parse_qsl(body.decode("utf-8"), keep_blank_values=True))
