import hashlib
import hmac

import aiohttp
from application.config import settings
from application.data.bruin import Email


async def notify_email(email: Email):
    await _notify(settings.notify_email_url, email)


async def notify_ticket(email: Email):
    await _notify(settings.notify_ticket_url, email)


async def _notify(url: str, email: Email):
    payload = email.json()
    signature = _signature_for(payload)
    headers = {"content-type": "application/json", "x-bruin-webhook-signature": signature}
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload, headers=headers)


def _signature_for(payload: str) -> str:
    payload_bytes = bytes("".join(payload), "utf-8")
    secret_key_bytes = bytes(settings.notify_key, "utf-8")
    signature = hmac.new(secret_key_bytes, payload_bytes, hashlib.sha256).hexdigest().upper()
    return signature
