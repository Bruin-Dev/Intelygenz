import requests
import json


class BruinTicketResponse:

    def __init__(self, logger, config, event_bus, bruin_client):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_client = bruin_client

    async def report_all_bruin_tickets(self, msg):
        msg_dict = json.loads(msg)
        self._logger.info("Sending all bruin tickets")
        ticket_id = ''
        if 'ticket_id' in msg_dict.keys():
            ticket_id = msg_dict['ticket_id']
        params = {
            "ClientId": msg_dict['client_id'],
            "TicketId": ticket_id
        }
        response = requests.get(f"{self._config['base_url']}/api/Ticket",
                                headers=self._bruin_client.get_request_headers(),
                                verify=False, params=params)
        filtered_tickets = [ticket for ticket in response.json()["responses"]
                            if "Closed" not in ticket["ticketStatus"]
                            if "Resolved" not in ticket["ticketStatus"]
                            if "SD-WAN" in ticket["category"]]
        filtered_tickets_response = {'request_id': msg_dict['request_id'], 'tickets': filtered_tickets,
                                     'status': response.status_code}
        await self._event_bus.publish_message(msg_dict['response_topic'],
                                              json.dumps(filtered_tickets_response, default=str))
        self._logger.info("All tickets sent")
