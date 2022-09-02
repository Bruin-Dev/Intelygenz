# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import logging
import os
import sys

from aiohttp import TraceConfig


def generate_aio_tracers(**kwargs):
    usage_repository = kwargs["endpoints_usage_repository"]

    async def bruin_usage_on_request_cb(session, trace_config_ctx, params):
        usage_repository.increment_usage(params.method, params.url.path, params.response.status)

    bruin_api_usage = TraceConfig()
    bruin_api_usage.on_request_end.append(bruin_usage_on_request_cb)

    AIOHTTP_CONFIG["tracers"] = [
        bruin_api_usage,
    ]


NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}


FORTICLOUD_CONFIG = {
    "base_url": os.environ["FORTICLOUD_BASE_URL"],
    "username": os.environ["FORTICLOUD_USERNAME"],
    "password": os.environ["FORTICLOUD_PASSWORD"],
    "client_id": os.environ["FORTICLOUD_CLIENT_ID"],
}

TIMEZONE = os.environ["TIMEZONE"]

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

LOG_CONFIG = {
    "name": "forticloud-bridge",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-forticloud-bridge"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

AIOHTTP_CONFIG = {"tracers": []}

QUART_CONFIG = {"title": "forticloud-bridge", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}