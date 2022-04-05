import hashlib
import hmac
import sys
import json
from typing import Dict
import random

import requests

SIGNATURE_SECRET_KEY = "dev-shared-secret-body-signature"
EMAIL_WEBHOOK_URL = "http://localhost:5055/api/email-tagger-webhook/email"


def random_email_id(payload_dict: Dict) -> Dict:
    random_email_id = random.randint(10000, 99999)
    payload_dict["Notification"]["Body"]["EmailId"] = random_email_id

    return payload_dict


def get_payload_from_file(json_file_name: str) -> Dict:
    with open(json_file_name) as file_:
        payload_dict = json.load(file_)
    return payload_dict


def calculate_signature(payload_str: str) -> str:
    payload_bytes = bytes("".join(payload_str), "utf-8")
    secret_key_bytes = bytes(SIGNATURE_SECRET_KEY, "utf-8")
    signature = hmac.new(secret_key_bytes, payload_bytes, hashlib.sha256).hexdigest()
    return signature.upper()


def main():
    json_file_name = sys.argv[1]

    payload_dict = get_payload_from_file(json_file_name)
    payload_dict = random_email_id(payload_dict)
    payload_str = json.dumps(payload_dict, indent=2)
    signature = calculate_signature(payload_str)

    headers = {
        "content-type": "application/json",
        "x-bruin-webhook-signature": signature,
    }

    print("Request to email-tagger-monitor:", EMAIL_WEBHOOK_URL, payload_dict, signature)
    response = requests.post(EMAIL_WEBHOOK_URL, data=payload_str, headers=headers)
    print("Response from email-tagger: ", response.status_code)


if __name__ == "__main__":
    main()
