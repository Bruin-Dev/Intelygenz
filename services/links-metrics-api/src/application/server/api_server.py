import os
import re
from http import HTTPStatus

from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from quart import jsonify, request
from quart_openapi import Pint

MEGABYTE: int = 1024 * 1024
MAX_CONTENT_LENGTH = 16 * MEGABYTE  # 16mb
SHA256_PREFIX = re.compile(r"^sha256=")


class APIServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, logger, config, get_link_metrics):
        self._config = config
        self._logger = logger
        self._get_link_metrics = get_link_metrics
        self._max_content_length = MAX_CONTENT_LENGTH
        self._title = config.QUART_CONFIG["title"]
        self._port = config.QUART_CONFIG["port"]

        self._endpoint_prefix = config.ENDPOINT_PREFIX

        self._hypercorn_config = HyperCornConfig()

        self._logger.info(f"env: {os.environ}")
        self._new_bind = f"0.0.0.0:{self._port}"
        self._app = Pint(__name__, title=self._title, no_openapi=True)
        API_REF = self._app

        @API_REF.route("/_health")
        async def _health():
            return jsonify(None), HTTPStatus.OK, None

        @API_REF.route(f"{self._endpoint_prefix}/metrics", methods=["GET"])
        async def _get_link_metrics():
            self._logger.info(f"Getting request: {request.url}")
            start_date = request.args.get("start_date")
            end_date = request.args.get("end_date")
            if not end_date or not start_date:
                return (
                    jsonify(
                        {
                            "error": "Request must have start_date and end_date as query params"
                            "start date and end date are integers representing milliseconds from epoch"
                            "in UTC"
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                    None,
                )
            json_res = await self._get_link_metrics.get_links_metrics(start_date, end_date)
            return jsonify(json_res), HTTPStatus.OK, None

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        self._logger.info(f"Starting API in port {self._port}")
        await serve(self._app, self._hypercorn_config)
