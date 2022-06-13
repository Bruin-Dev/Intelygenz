from dataclasses import dataclass
from http import HTTPStatus
from typing import Union

from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from quart import Quart, jsonify


@dataclass
class Config:
    port: Union[int, str]
    host: str = "0.0.0.0"


class Server:
    """
    Sets up a Quart server with a pre-routed /_health endpoint for health checks
    """

    server = Quart(__name__)

    def __init__(self, config: Config):
        self._hypercorn_config = HyperCornConfig()
        self._hypercorn_config.bind = [f"{config.host}:{config.port}"]

    async def run(self):
        """
        Runs the Quart server according to the configuration.
        """
        await serve(self.server, self._hypercorn_config)

    @server.route("/_health", methods=["GET"])
    async def __health():
        """
        Simple endpoint that replies with an HTTP 200 on every call. Useful for periodic health checks.
        """
        return jsonify(None), HTTPStatus.OK, None
