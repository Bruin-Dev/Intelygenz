import asyncio
import json
import signal

from quart import Quart, request

from integration_tests.conftest import MockServer


class BruinMockServer(MockServer):
    def __post_init__(self):
        self.server = Quart("mock-server")
        self.server.add_url_rule(
            "/api/v1/networks/584558/fap/access_points/FP221E5521072717/", view_func=self.test_ap, methods=["GET"]
        )
        self.server.add_url_rule("/api/v1/auth", view_func=self.auth, methods=["POST"])

    async def test_ap(self):
        print(f"path={request.path}, body={await request.body}")
        response = {
            "result": {
                "connection_state": "disconnected",
                "name": "test device",
                "disc_type": "test model",
                "serial": "FP221E5521072717",
            }
        }

        return json.dumps(response), 200, {"content-type": "text/plain"}

    async def auth(self):
        print(f"path={request.path}, body={await request.body}")
        response = {"access_token": "any_access_token", "expires_in": 10000}
        return json.dumps(response), 200, {"Content-type": "application/json"}


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    mock_server = BruinMockServer(["0.0.0.0:8010"])

    async def close():
        await mock_server.close()
        asyncio.get_running_loop().stop()

    loop.create_task(mock_server.start(loop))
    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(close()))
    loop.run_forever()
