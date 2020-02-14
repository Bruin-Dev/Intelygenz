import json


class GetTicket:

    def __init__(self, logger, config, event_bus, bruin_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_repository = bruin_repository

    async def get_all_tickets(self, msg: dict):
        filtered_tickets_response = {
            'request_id': msg['request_id'],
            'tickets': None,
            'status': None
        }

        if msg.get("params") and msg.get("ticket_status"):

            ticket_status = msg['ticket_status']

            ticket_id = ''
            if 'ticket_id' in msg['params'].keys():
                ticket_id = msg['params']['ticket_id']

            msg['params']['ticket_id'] = ticket_id

            params = msg['params']

            if not all(key in params.keys() for key in ("client_id", "category", "ticket_topic")):
                self._logger.info(f'Cannot get tickets  using {json.dumps(params)}. '
                                  f'Need "client_id", "category", "ticket_topic"')
                filtered_tickets_response["status"] = 400
                filtered_tickets_response["tickets"] = 'You must specify "client_id", "category", ' \
                                                       '"ticket_topic" in the params'
                await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
                return

            self._logger.info(f'Collecting all tickets for client id: {params["client_id"]}...')

            filtered_tickets = self._bruin_repository.get_all_filtered_tickets(params, ticket_status)

            filtered_tickets_response['tickets'] = filtered_tickets["body"]
            filtered_tickets_response["status"] = filtered_tickets["status"]

            self._logger.info(f'All tickets for client id: {params["client_id"]} sent')

        else:
            filtered_tickets_response["status"] = 400
            filtered_tickets_response["tickets"] = 'You must specify ' \
                                                   '{.."params":{"client_id", "category", "ticket_topic"},' \
                                                   ' "ticket_status":[list of statuses]...} in the request'
        await self._event_bus.publish_message(msg['response_topic'], filtered_tickets_response)
