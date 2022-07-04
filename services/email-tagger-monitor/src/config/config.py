# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import logging
import os
import sys

NATS_CONFIG = {
    "servers": [os.environ["NATS_SERVER1"]],
    "subscriber": {"pending_limits": 65536},
    "multiplier": 5,
    "min": 5,
    "stop_delay": 300,
    "reconnects": 150,
}

TIMEZONE = os.environ["TIMEZONE"]

MONITOR_CONFIG = {
    "max_retries_error_404": 5,
    "scheduler_config": {
        "new_emails_seconds": int(os.environ["NEW_EMAILS_JOB_INTERVAL"]),
        "new_tickets_seconds": int(os.environ["NEW_TICKETS_JOB_INTERVAL"]),
    },
    "nats_request_timeout": {"kre_seconds": 10, "post_email_tag_seconds": 30},
    "semaphores": {
        "new_emails_concurrent": int(os.environ["MAX_CONCURRENT_EMAILS"]),
        "new_tickets_concurrent": int(os.environ["MAX_CONCURRENT_TICKETS"]),
    },
    "api_server": {
        "schema_path": "./src/schema.json",
        "swagger_path": "./src/swagger.yml",
        "swagger_url_prefix": "/api/doc",
        "swagger_title": "Email Tagger API Docs",
        "request_signature_secret_key": os.environ["API_REQUEST_SIGNATURE_SECRET_KEY"],
        "use_request_api_key_header": False,
        "request_api_key": os.environ["API_REQUEST_KEY"],
        "endpoint_prefix": os.environ["API_ENDPOINT_PREFIX"],
    },
    "reply_email_ttl": int(os.environ["REPLY_EMAIL_TTL"])
}

CURRENT_ENVIRONMENT = os.environ["CURRENT_ENVIRONMENT"]
ENVIRONMENT_NAME = os.environ["ENVIRONMENT_NAME"]

LOG_CONFIG = {
    "name": "email-tagger-monitor",
    "level": logging.DEBUG,
    "stream_handler": logging.StreamHandler(sys.stdout),
    "format": f"%(asctime)s: {ENVIRONMENT_NAME}: %(hostname)s: %(module)s::%(lineno)d %(levelname)s: %(message)s",
    "papertrail": {
        "active": os.environ["PAPERTRAIL_ACTIVE"] == "true",
        "prefix": os.getenv("PAPERTRAIL_PREFIX", f"{ENVIRONMENT_NAME}-email-tagger-monitor"),
        "host": os.environ["PAPERTRAIL_HOST"],
        "port": int(os.environ["PAPERTRAIL_PORT"]),
    },
}

QUART_CONFIG = {"title": "email-tagger-monitor", "port": 5000}

REDIS = {"host": os.environ["REDIS_HOSTNAME"]}

REDIS_CACHE = {"host": os.environ["REDIS_EMAIL_TAGGER_HOSTNAME"]}

METRICS_SERVER_CONFIG = {"port": 9090}
