import json
import logging

from nats.aio.msg import Msg

logger = logging.getLogger(__name__)


class GetTestResults:
    def __init__(self, hawkeye_repository):
        self._hawkeye_repository = hawkeye_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)
        probes_response = {"request_id": payload["request_id"], "body": None, "status": None}
        body = payload.get("body")
        if body is None:
            logger.error(f"Cannot get probe's tests using {json.dumps(payload)}. JSON malformed")
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "body" in request'
            await msg.respond(data=json.dumps(probes_response).encode())
            return

        if "probe_uids" not in body:
            logger.error(
                f"Cannot get probe's tests using {json.dumps(body)}. "
                f"Must include 'probe_uids' in the body of the request"
            )
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "probe_uids" in the body of the request'
            await msg.respond(data=json.dumps(probes_response).encode())
            return
        if "interval" not in body:
            logger.error(
                f"Cannot get probe's tests using {json.dumps(body)}. "
                f"Must include 'interval' in the body of the request"
            )
            probes_response["status"] = 400
            probes_response["body"] = 'Must include "interval" in the body of the request'
            await msg.respond(data=json.dumps(probes_response).encode())
            return

        logger.info(
            f"Collecting all test results with filters: "
            f"{json.dumps(body['probe_uids'])} {json.dumps(body['interval'])}..."
        )

        filtered_tests = await self._hawkeye_repository.get_test_results(body["probe_uids"], body["interval"])

        filtered_tests_response = {**probes_response, **filtered_tests}

        await msg.respond(data=json.dumps(filtered_tests_response).encode())
