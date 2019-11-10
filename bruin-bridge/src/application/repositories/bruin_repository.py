class BruinRepository:

    def __init__(self, logger, bruin_client):
        self._logger = logger
        self._bruin_client = bruin_client

    def get_all_filtered_tickets(self, client_id, ticket_id, ticket_status, category, ticket_topic):
        ticket_list = []
        for status in ticket_status:
            status_ticket_list = self._bruin_client.get_all_tickets(client_id, ticket_id, status, category,
                                                                    ticket_topic)
            if status_ticket_list is not None:
                ticket_list = ticket_list + status_ticket_list
            else:
                return None
        if len(ticket_list) > 0:
            return list({ticket_id['ticketID']: ticket_id for ticket_id in ticket_list}.values())
        return []

    def get_ticket_details(self, ticket_id):
        return self._bruin_client.get_ticket_details(ticket_id)

    def get_ticket_details_by_edge_serial(self, edge_serial, client_id,
                                          ticket_topic, category='SD-WAN',
                                          ticket_statuses=None):
        result = []

        filtered_tickets = self.get_all_filtered_tickets(
            client_id=client_id, category=category, ticket_topic=ticket_topic,
            ticket_id=None, ticket_status=ticket_statuses,
        )

        for ticket in filtered_tickets:
            ticket_id = ticket['ticketID']
            ticket_details_dict = self.get_ticket_details(ticket_id)

            ticket_details_items = ticket_details_dict['ticketDetails']
            ticket_details_items_as_booleans = map(
                lambda ticket_detail: ticket_detail['detailValue'] == edge_serial,
                ticket_details_items,
            )
            if any(ticket_details_items_as_booleans):
                result.append({
                    'ticketID': ticket_id,
                    **ticket_details_dict,
                })

        return result

    def post_ticket_note(self, ticket_id, note):
        return self._bruin_client.post_ticket_note(ticket_id, note)

    def post_ticket(self, client_id, category, services, notes, contacts):
        return self._bruin_client.post_ticket(client_id, category, services, notes, contacts)
