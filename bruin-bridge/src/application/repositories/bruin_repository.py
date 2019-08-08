class BruinRepository:

    def __init__(self, logger, bruin_client):
        self._logger = logger
        self._bruin_client = bruin_client

    def get_all_filtered_tickets(self, client_id, ticket_id, ticket_status, category):
        return self._bruin_client.get_all_tickets(client_id, ticket_id, ticket_status, category)

    def get_ticket_details(self, ticket_id):
        return self._bruin_client.get_ticket_details(ticket_id)

    def post_ticket_note(self, ticket_id, note):
        return self._bruin_client.post_ticket_note(ticket_id, note)
