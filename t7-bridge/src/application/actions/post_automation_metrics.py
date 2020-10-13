import json


class PostAutomationMetrics:

    def __init__(self, logger, config, event_bus, t7_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_repository = t7_repository

    async def post_automation_metrics(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }

        msg_body = msg.get('body')
        if not msg_body:
            self._logger.error(f'Cannot post automation metrics using {json.dumps(msg)}. JSON malformed')
            response['body'] = 'You must specify {.."body": {"ticket_id": "...", "ticket_rows";[...]}..} in the request'
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        if not all(key in msg_body.keys() for key in ("ticket_id", "ticket_rows")):
            self._logger.error(f'Cannot post automation metrics using {json.dumps(msg_body)}. '
                               'Need parameter "ticket_id" and "ticket_rows"')
            response['body'] = 'You must specify {"ticket_id": "...", "ticket_rows";[...]} in the body'
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        post_metrics_response = self._t7_repository.post_automation_metrics(msg_body)
        response = {
            'request_id': msg['request_id'],
            'body': post_metrics_response["body"],
            'status': post_metrics_response["status"],
            'kre_response': post_metrics_response["kre_response"]
        }

        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Metrics posted for ticket {msg_body["ticket_id"]} published in event bus!')
