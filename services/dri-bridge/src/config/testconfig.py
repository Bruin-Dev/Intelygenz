# You must replicate the structure of config.py, changing os.environ calls for mock values
import logging
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
    "servers": "nats://nats-server:4222",
    "client_ID": "base-microservice",
    "subscriber": {"pending_limits": 65536},
    "publisher": {"max_pub_acks_inflight": 6000},
    "multiplier": 0.1,
    "min": 0,
    "stop_delay": 0.4,
    "reconnects": 0,
}

DRI_CONFIG = {
    "base_url": "some.dri.url",
    "email_acc": "some@email.acc",
    "email_password": "some.email.password",
    "redis_save_ttl": 300,
}

ENVIRONMENT_NAME = "dev"

LOG_CONFIG = {
    "name": "dri-bridge-test",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": "%(asctime)s: %(module)s: %(levelname)s: %(message)s",
}
