import hashlib
import hmac
import sys

import requests

SIGNATURE_SECRET_KEY = "dev-shared-secret-body-signature"
EMAIL_WEBHOOK_URL = "http://localhost:5055/api/email-tagger-webhook/ticket"


def get_payload_from_file(json_file_name: str):
    with open(json_file_name) as file_:
        webhook_content = file_.readlines()
    return "".join(webhook_content)


def calculate_signature(payload: str):
    payload_bytes = bytes("".join(payload), "utf-8")
    secret_key_bytes = bytes(SIGNATURE_SECRET_KEY, "utf-8")
    signature = hmac.new(secret_key_bytes, payload_bytes, hashlib.sha256).hexdigest()
    return signature.upper()


def main():
    json_file_name = sys.argv[1]

    payload = get_payload_from_file(json_file_name)
    signature = calculate_signature(payload)

    headers = {
        "content-type": "application/json",
        "x-bruin-webhook-signature": signature,
    }

    print("Request to email-tagger-monitor:", EMAIL_WEBHOOK_URL, payload, signature)
    response = requests.post(EMAIL_WEBHOOK_URL, data=payload, headers=headers)
    print("Response from email-tagger: ", response.status_code)


if __name__ == "__main__":
    main()
