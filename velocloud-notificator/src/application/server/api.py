from quart_openapi import Pint, Resource
from http import HTTPStatus


quart_server = Pint(__name__, title='velocloud-notificator-api')


@quart_server.route('/')
class HealthCheck(Resource):
    async def get(self):
        return '', HTTPStatus.OK, None
