import os
import re
from http import HTTPStatus

from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from quart import jsonify
from quart_openapi import Pint

MEGABYTE: int = (1024 * 1024)
MAX_CONTENT_LENGTH = 32 * MEGABYTE  # 32mb
SHA256_PREFIX = re.compile(r"^sha256=")


class APIServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, logger, config):
        self._config = config
        self._logger = logger

        self._max_content_length = MAX_CONTENT_LENGTH
        self._title = config.QUART_CONFIG['title']
        self._port = config.QUART_CONFIG['port']

        self._endpoint_prefix = config.ENDPOINT_PREFIX

        self._hypercorn_config = HyperCornConfig()

        self._logger.info(f'env: {os.environ}')
        self._new_bind = f'0.0.0.0:{self._port}'
        self._app = Pint(__name__, title=self._title, no_openapi=True)

        self.register_endpoints()

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        self._logger.info(f"Starting API in port {self._port}")
        await serve(self._app, self._hypercorn_config)

    def register_endpoints(self):
        self._app.add_url_rule("/_health", None, self._health)
        self._app.add_url_rule(self._endpoint_prefix + "/metrics", None, self._test_method, methods=['GET'],
                               strict_slashes=False)

    # Endpoints
    def _health(self):
        return jsonify(None), HTTPStatus.OK, None

    async def _test_method(self):
        json_response = {"message": "Hello world, this is a placeholder!"}
        return jsonify(json_response), HTTPStatus.OK, None
