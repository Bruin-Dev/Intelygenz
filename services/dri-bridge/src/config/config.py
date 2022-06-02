# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import logging
import os
import sys

from aiohttp import TraceConfig


def generate_aio_tracers(**kwargs):
    usage_repository = kwargs["endpoints_usage_repository"]

    async def dri_usage_on_request_cb(session, trace_config_ctx, params):
        usage_repository.increment_usage(params.method, params.url.path)

    dri_api_usage = TraceConfig()
    dri_api_usage.on_request_start.append(dri_usage_on_request_cb)

    AIOHTTP_CONFIG["tracers"] = [
        dri_api_usage,
    ]


AIOHTTP_CONFIG = {"tracers": []}

METRICS_SERVER_CONFIG = {"port": 9090}

NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

DRI_CONFIG = {
    "base_url": os.environ["BASE_URL"],
    "email_acc": os.environ["USERNAME"],
    "email_password": os.environ["PASSWORD"],
    "redis_save_ttl": int(os.environ["DRI_DATA_REDIS_TTL"]),
}

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

LOG_CONFIG = {
    "name": "dri-bridge",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-dri-bridge"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "dri-bridge", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}
