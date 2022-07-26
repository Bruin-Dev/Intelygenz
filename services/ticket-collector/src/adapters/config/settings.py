import logging
import os
import sys

from dotenv import load_dotenv

ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]
CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]

LOG_CONFIG = {
    "name": "ticket-collector",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-ticket-collector"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "ticket-collector", "port": 5000}

METRICS_SERVER_CONFIG = {"port": 9090}


def get_config():
    APP_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")  # refers to application_top
    dotenv_path = os.path.join(APP_ROOT, "config/.env")
    load_dotenv(dotenv_path)

    mongo_user = os.environ["MONGODB_USERNAME"]
    mongo_password = os.environ["MONGODB_PASSWORD"]
    mongo_host = os.environ["MONGODB_HOST"]
    mongo_db = os.environ["MONGODB_DATABASE"]
    mongo_params = get_mongo_params()
    mongo_url = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}/{mongo_db}?{mongo_params}"

    return {
        "environment_name": ENVIRONMENT_NAME,
        "current_environment": CURRENT_ENVIRONMENT,
        "sentry": {"config": {"release": os.getenv("VERSION")}, "dsn": os.getenv("SENTRY_DSN")},
        "mongo": {"url": mongo_url},
        "bruin": {"id": os.environ["BRUIN_CLIENT_ID"], "secret": os.environ["BRUIN_CLIENT_SECRET"]},
        "job_interval_hours": 4,
        "days_to_retrieve": 3,
        "days_to_update": 3,
        "concurrent_days": 1,
    }


def get_mongo_params():
    if ENVIRONMENT_NAME.endswith("local"):
        return "authSource=admin"
    else:
        return (
            "ssl=true&ssl_ca_certs=/rds-combined-ca-bundle.pem"
            "&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
        )
