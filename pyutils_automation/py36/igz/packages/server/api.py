from quart import jsonify, Quart
from http import HTTPStatus
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig


class QuartServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None
    _quart_server = Quart(__name__)

    def __init__(self, config):
        self._title = config.QUART_CONFIG['title']
        self._port = config.QUART_CONFIG['port']
        self._hypercorn_config = HyperCornConfig()
        self._new_bind = f'0.0.0.0:{self._port}'
        self._quart_server.title = self._title
        self._status = HTTPStatus.OK

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        self.add_routes()
        await serve(self._quart_server, self._hypercorn_config)

    def add_routes(self):
        self._quart_server.add_url_rule("/_health", None, self.health)

    def set_status(self, status):
        self._status = status

    def health(self):
        return jsonify(None), self._status, None
