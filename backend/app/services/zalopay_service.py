
import httpx
import json
import hmac
import hashlib
import time
from typing import Any

from app.core.config import settings


class ZaloPayService:

    def __init__(self):
        self.app_id = settings.zalopay_appid
        self.key1 = settings.zalopay_key1
        self.key2 = settings.zalopay_key2
        self.endpoint = settings.zalopay_endpoint
        self.redirect_url = settings.zalopay_redirect_url

    # CREATE ORDER
    async def create_order(
        self,
        amount: int,
        app_user: str,
        app_trans_id: str,
        description: str,
        items: list[dict[str, Any]]
    ):

        app_time = int(time.time() * 1000)

        item_data = json.dumps(
            items,
            ensure_ascii=False
        )

        embed_data = json.dumps(
            {"redirecturl": self.redirect_url},
            ensure_ascii=False
        )

        order_data = {
            "appid": self.app_id,
            "appuser": app_user,
            "apptime": app_time,
            "apptransid": app_trans_id,
            "item": item_data,
            "embeddata": embed_data,
            "amount": amount,
            "description": description,
            "bankcode": ""
        }

        mac_data = "|".join([
            str(order_data["appid"]),
            order_data["apptransid"],
            order_data["appuser"],
            str(order_data["amount"]),
            str(order_data["apptime"]),
            order_data["embeddata"],
            order_data["item"]
        ])

        order_data["mac"] = hmac.new(
            self.key1.encode("utf-8"),
            mac_data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        async with httpx.AsyncClient(timeout=15.0) as client:

            response = await client.post(
                self.endpoint,
                data=order_data
            )

            response.raise_for_status()

            return response.json()

    # VERIFY CALLBACK
    def verify_callback(self, callback_data: dict):

        data = callback_data.get("data")
        mac = callback_data.get("mac")

        if not data or not mac:
            return None

        calculated_mac = hmac.new(
            self.key2.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_mac, mac):
            return None

        return json.loads(data)

    # QUERY PAYMENT STATUS
    async def get_payment_status(self, app_trans_id: str):

        mac_data = f"{self.app_id}|{app_trans_id}|{self.key1}"

        mac = hmac.new(
            self.key1.encode("utf-8"),
            mac_data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        params = {
            "appid": self.app_id,
            "apptransid": app_trans_id,
            "mac": mac
        }

        async with httpx.AsyncClient(timeout=15.0) as client:

            response = await client.post(
                "https://sandbox.zalopay.com.vn/v001/tpe/getstatusbyapptransid",
                data=params
            )

            response.raise_for_status()

            return response.json()
