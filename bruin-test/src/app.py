import base64
import json
import logging as _logger
import os
from datetime import datetime

import asyncio
import humps
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from igz.packages.server.api import QuartServer

from config import config

_logger.basicConfig(format='%(levelname)s:%(message)s', level=_logger.INFO)

BEARER_TOKEN = None
CLIENT_ID = os.environ["BRUIN_CLIENT_ID"]
CLIENT_SECRET = os.environ["BRUIN_CLIENT_SECRET"]
LOGIN_URL = os.environ["BRUIN_LOGIN_URL"]
BASE_URL = os.environ["BRUIN_BASE_URL"]
scheduler = AsyncIOScheduler()
quart_server = QuartServer(config)


# Login Bruin Client
def login():
    global BEARER_TOKEN
    _logger.info("Logging into Bruin...")
    creds = str.encode(CLIENT_ID + ":" + CLIENT_SECRET)
    headers = {
        "authorization": f"Basic {base64.b64encode(creds).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    form_data = {
        "grant_type": "client_credentials",
        "scope": "public_api"
    }

    try:
        response = requests.post(f'{LOGIN_URL}/identity/connect/token',
                                 data=form_data,
                                 headers=headers)
        BEARER_TOKEN = response.json()["access_token"]
        _logger.info(f"Response from Bruin{response.json()}")
        _logger.info("Logged into Bruin!")

    except Exception as err:
        _logger.error("An error occurred while trying to login to Bruin")
        _logger.error(f"{err}")


def get_request_headers():
    if not BEARER_TOKEN:
        _logger.info("No bearer token present. Loggin in")
        login()

    headers = {
        "authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json-patch+json",
        "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
    }
    return headers


def get_client_info(filters):
    try:
        _logger.info(f'Getting Bruin client ID for filters: {filters}')
        parsed_filters = humps.pascalize(filters)
        return_response = dict.fromkeys(["body", "status"])

        try:
            response = requests.get(f'{BASE_URL}/api/Inventory',
                                    headers=get_request_headers(),
                                    params=parsed_filters,
                                    verify=False)
        except ConnectionError as e:
            _logger.error(f"A connection error happened while trying to connect to Bruin API. {e}")
            return_response["body"] = f"Connection error in Bruin API. {e}"
            return_response["status"] = 500
            return return_response

        if response.status_code in range(200, 300):
            return_response["body"] = response.json()
            return_response["status"] = response.status_code

        if response.status_code == 400:
            return_response["body"] = response.json()
            return_response["status"] = response.status_code
            _logger.error(f"Got error from Bruin {response.json()}")

        if response.status_code == 401:
            _logger.info(f"Got 401 from Bruin, re-login and retrying")
            login()

            return_response["body"] = f"Got Unauthorized from Bruin"
            return_response["status"] = 401
            raise Exception(return_response)

        if response.status_code in range(500, 513):
            return_response["body"] = f"Got internal error from Bruin"
            return_response["status"] = 500

        return return_response

    except Exception as e:
        return e.args[0]


def test_call():
    res = get_client_info({"client_id": 84816})
    _logger.info(f'Response from bruin: {json.dumps(res, indent=2)}')
    _logger.info("Response should start with : {'body': {'documents':...")


def schedule_test():
    minutes = 5
    _logger.info(f'Bruin test scheduled to run each {minutes} minutes')
    scheduler.add_job(test_call, 'interval', minutes=minutes, replace_existing=False,
                      id='_edge_monitoring_process', misfire_grace_time=9999)


async def _start():
    scheduler.start()
    test_call()
    schedule_test()


async def start_server():
    await quart_server.run_server()


async def run():
    await _start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(run(), loop=loop)
    asyncio.ensure_future(start_server(), loop=loop)
    loop.run_forever()
