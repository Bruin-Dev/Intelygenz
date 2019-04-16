from quart import jsonify
from quart_openapi import Pint, Resource
from http import HTTPStatus
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig


class QuartServer:

    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None
    _quart_server = Pint(__name__)

    def __init__(self, config):
        self._title = config.QUART_CONFIG['title']
        self._port = config.QUART_CONFIG['port']
        self._hypercorn_config = HyperCornConfig()
        self._new_bind = f'0.0.0.0:{self._port}'
        self._quart_server.title = self._title

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        await serve(self._quart_server, self._hypercorn_config)

    @_quart_server.route('/_health')
    class HealthCheck(Resource):
        async def get(self):
            return jsonify(None), HTTPStatus.OK, None
