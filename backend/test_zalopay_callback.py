
import asyncio
import hashlib
import hmac
import json
import time

import httpx

from app.core.config import settings


async def main():
    app_trans_id = input("App transaction ID: ").strip()
    amount = int(input("Transaction amount: ").strip())

    callback_info = {
        "app_id": settings.zalopay_appid,
        "app_trans_id": app_trans_id,
        "amount": amount,
        "zp_trans_id": 123456789,
        "server_time": int(time.time() * 1000)
    }

    data = json.dumps(
        callback_info,
        separators=(",", ":"),
        ensure_ascii=False
    )

    mac = hmac.new(
        settings.zalopay_key2.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    payload = {
        "data": data,
        "mac": mac,
        "type": 1
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "http://127.0.0.1:8000/payments/callback",
            json=payload
        )

        print("HTTP Status:", response.status_code)
        print("Response:", response.json())


if __name__ == "__main__":
    asyncio.run(main())
