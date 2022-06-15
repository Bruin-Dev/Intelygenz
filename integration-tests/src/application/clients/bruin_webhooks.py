import hashlib
import hmac

import aiohttp
from application.config import settings
from application.scenarios.models.email import Email


async def notify_email(email: Email):
    payload = email.json()
    signature = signature_for(payload)
    headers = {"content-type": "application/json", "x-bruin-webhook-signature": signature}
    async with aiohttp.ClientSession() as session:
        await session.post(settings.notify_email_url, data=payload, headers=headers)


def signature_for(payload: str) -> str:
    payload_bytes = bytes("".join(payload), "utf-8")
    secret_key_bytes = bytes(settings.notify_email_key, "utf-8")
    signature = hmac.new(secret_key_bytes, payload_bytes, hashlib.sha256).hexdigest().upper()
    return signature
