import asyncio
import json
import signal
import time

from quart import Quart, request

from integration_tests.conftest import MockServer


class BruinMockServer(MockServer):
    def __post_init__(self):
        self.server = Quart("mock-server")
        self.server.add_url_rule("/api/Ticket/repair", view_func=self.ticket_repair, methods=["POST"])
        self.server.add_url_rule("/api/Ticket/<ticket_id>/notes", view_func=self.ticket_note, methods=["POST"])

    async def ticket_repair(self):
        print(f"bruin-mock: path={request.path}, body={await request.body}")
        response = {"assets": [{"ticketId": round(time.time() * 1000)}]}
        return json.dumps(response), 200, {"Content-type": "application/json"}

    async def ticket_note(self, ticket_id: str):
        print(f"bruin-mock: path={request.path}, body={await request.body}")
        return ""


if __name__ == "__main__":
    print("Hey!")
    loop = asyncio.new_event_loop()
    mock_server = BruinMockServer(["0.0.0.0:8010"])

    async def close():
        await mock_server.close()
        asyncio.get_running_loop().stop()

    loop.create_task(mock_server.start(loop))
    loop.add_signal_handler(signal.SIGINT, lambda: loop.create_task(close()))
    loop.run_forever()
