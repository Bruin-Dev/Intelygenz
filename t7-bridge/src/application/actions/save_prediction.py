import json


class SavePrediction:

    def __init__(self, logger, config, event_bus, t7_kre_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._t7_kre_repository = t7_kre_repository

    async def save_prediction(self, msg: dict):
        request_id = msg['request_id']
        response_topic = msg['response_topic']
        response = {
            'request_id': request_id,
            'body': None,
            'status': None
        }

        msg_body = msg.get('body')
        if not msg_body:
            self._logger.error(f'Cannot save prediction using {json.dumps(msg)}. JSON malformed')
            response['body'] = (
                'You must specify {.."body": {"ticket_id", "ticket_rows", "predictions", "available_options" and'
                ' "suggested_notes"}..} in the request'
            )
            response['status'] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        ticket_id = msg_body.get('ticket_id')
        ticket_rows = msg_body.get('ticket_rows')
        predictions = msg_body.get('predictions')
        available_options = msg_body.get('available_options')
        suggested_notes = msg_body.get('suggested_notes')

        if not ticket_id or not ticket_rows or not predictions or not available_options or not suggested_notes:
            self._logger.error(
                'You must specify {.."body": {"ticket_id", "ticket_rows", "predictions", "available_options" and'
                ' "suggested_notes"}..} in the request'
            )

            response["body"] = (
                'You must specify {.."body": {"ticket_id", "ticket_rows", "predictions", "available_options" and'
                ' "suggested_notes"} in the request'
            )
            response["status"] = 400
            await self._event_bus.publish_message(response_topic, response)
            return

        response["body"] = f'Save prediction request for ticket_id[{ticket_id}] was sent to KRE'
        response["status"] = 200
        await self._event_bus.publish_message(msg['response_topic'], response)
        self._logger.info(f'Save prediction for ticket {ticket_id} published in event bus!')

        save_kre_prediction_response = self._t7_kre_repository.save_prediction(
            ticket_id, ticket_rows, predictions, available_options, suggested_notes
        )

        if save_kre_prediction_response["status"] == 200:
            msg = (
                f"KRE save prediction for ticket {msg_body['ticket_id']}"
            )
            self._logger.info(msg)
        else:
            msg = (
                f"ERROR on KRE saving prediction for ticket_id[{msg_body['ticket_id']}]:"
                f"Body: {save_kre_prediction_response['body']}, Status: {save_kre_prediction_response['status']}"
            )
            self._logger.error(msg)
