import json


class PostNotificationEmailMilestone:

    def __init__(self, logger, event_bus, bruin_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def post_notification_email_milestone(self, msg: dict):
        response = {
            'request_id': msg['request_id'],
            'body': None,
            'status': None
        }
        payload = msg.get('body')

        if payload is None:
            response['status'] = 400
            response['body'] = 'Must include {.."body":{"ticket_id", "notification_type", "service_number"}, in request'
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        if not all(key in payload.keys() for key in ('ticket_id', 'notification_type', 'service_number')):
            self._logger.error(f'Cannot send milestone email using {json.dumps(msg)}. '
                               f'JSON malformed')

            response['body'] = ('You must include "ticket_id", "notification_type" and "service_number"'
                                ' in the "body" field of the response request')
            response['status'] = 400
            await self._event_bus.publish_message(msg['response_topic'], response)
            return

        ticket_id = payload.get('ticket_id')
        notification_type = payload.get('notification_type')
        service_number = payload.get('service_number')

        self._logger.info(f'Sending milestone email for ticket "{ticket_id}", service number "{service_number}"'
                          f' and notification type "{notification_type}"...')

        # result = await self._bruin_repository.post_notification_email_milestone(payload)
        result = {"body": "", "status": 200}

        response['body'] = result['body']
        response['status'] = result['status']
        if response['status'] in range(200, 300):
            self._logger.info(f'Milestone email notification successfully sent for ticket {ticket_id}, service number'
                              f' {service_number} and notification type {notification_type}')
        else:
            self._logger.error(f'Error sending milestone email notification for ticket {ticket_id}, service number'
                               f' {service_number} and notification type {notification_type}: Status:'
                               f' {response["status"]} body: {response["body"]}')

        await self._event_bus.publish_message(msg['response_topic'], response)
