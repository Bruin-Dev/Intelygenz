from quart import jsonify
from quart_openapi import Pint, Resource
from http import HTTPStatus
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig


class QuartServer:

    _title = None
    _quart_server = None
    _port = None

    def __init__(self, config):
        self._title = config.QUART_CONFIG['title']
        self._port = config.QUART_CONFIG['port']
        self._quart_server = Pint(__name__, title=self._title)

    async def run_server(self):
        corn_config = HyperCornConfig()
        new_bind = f'0.0.0.0:{self._port}'
        corn_config.bind = [new_bind]
        await serve(self._quart_server, corn_config)

    @_quart_server.route('/')
    class HealthCheck(Resource):
        async def get(self):
            return jsonify(None), HTTPStatus.OK, None
