from http import HTTPStatus

from quart import Quart, jsonify
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from quart_openapi import Pint
from swagger_ui import quart_api_doc


class DispatchServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, config, redis_client, event_bus, logger):
        self._config = config
        self._title = config.DISPATCH_PORTAL_CONFIG['title']
        self._port = config.DISPATCH_PORTAL_CONFIG['port']
        self._hypercorn_config = HyperCornConfig()
        self._new_bind = f'0.0.0.0:{self._port}'
        self._quart_server = Pint(__name__, title=self._title)
        self._quart_server._redis_client = redis_client
        self._quart_server._event_bus = event_bus
        self._quart_server._logger = logger
        self._status = HTTPStatus.OK
        self._quart_server.add_url_rule("/_health", None, self.health)

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        await serve(self._quart_server, self._hypercorn_config)

    def attach_swagger(self):
        quart_api_doc(self._quart_server,
                      config_path=self._config.DISPATCH_PORTAL_CONFIG['swagger_path'],
                      url_prefix=self._config.DISPATCH_PORTAL_CONFIG['swagger_url_prefix'],
                      title=self._config.DISPATCH_PORTAL_CONFIG['swagger_title'])

    def register_blueprint(self, bp):
        self._quart_server.register_blueprint(bp)

    def health(self):
        return jsonify(None), self._status, None
