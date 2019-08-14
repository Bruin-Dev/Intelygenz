class BruinRepository:

    def __init__(self, logger, bruin_client):
        self._logger = logger
        self._bruin_client = bruin_client

    def get_all_filtered_tickets(self, client_id, ticket_id, ticket_status, category):
        ticket_list = []
        for status in ticket_status:
            status_ticket_list = self._bruin_client.get_all_tickets(client_id, ticket_id, status, category)
            if status_ticket_list is not None:
                ticket_list = ticket_list + status_ticket_list
        if len(ticket_list) > 0:
            return ticket_list
        return None

    def get_ticket_details(self, ticket_id):
        return self._bruin_client.get_ticket_details(ticket_id)

    def post_ticket_note(self, ticket_id, note):
        return self._bruin_client.post_ticket_note(ticket_id, note)
