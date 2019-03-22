from quart_openapi import Pint, Resource

app = Pint(__name__, title='Sample App')


@app.route('/')
class HealthChecks(Resource):
    async def get(self):
        return "Success"
