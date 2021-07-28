from typing import List


class NewTicketsRepository:
    def __init__(self, logger, config, notifications_repository, storage_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
        self._storage_repository = storage_repository
        self.TICKET_PREFIX = self._config.MONITOR_CONFIG["prefixes"]["ticket_prefix"]

    def validate_ticket(self, ticket: dict) -> bool:
        if not ticket:
            return False
        elif 'email' not in ticket or not ticket['email'] or 'ticket' not in ticket or not ticket['ticket']:
            return False
        elif 'email' not in ticket['email'] or not ticket['email']['email']:
            return False
        elif ('email_id' not in ticket['email']['email'] or not ticket['email']['email']['email_id']) or (
                'client_id' not in ticket['email']['email'] or not ticket['email']['email']['client_id']):
            return False
        elif 'ticket_id' not in ticket['ticket'] or not ticket['ticket']['ticket_id']:
            return False

        return True

    def get_pending_tickets(self) -> List[dict]:
        filtered_tickets = []
        all_tickets = self._storage_repository.find_all(self.TICKET_PREFIX)
        self._logger.info(f"Checking for valid tickets {len(all_tickets)}")
        for ticket in all_tickets:
            if self.validate_ticket(ticket):
                filtered_tickets.append(ticket)
            else:
                self._logger.info(f"Ticket not valid be processed. [{ticket}]")
        return filtered_tickets

    def save_new_ticket(self, email_data: dict, ticket_data: dict):
        email_id = email_data['email']['email_id']
        ticket_id = ticket_data['ticket_id']
        self._logger.info(f"adding email data '{email_id}' and '{ticket_id}'")
        key = f"ticket_{email_id}_{ticket_id}"
        self._storage_repository.save(key, {"email": email_data, "ticket": ticket_data})

    def mark_complete(self, email_id: str, ticket_id: str):
        self._logger.info(f"marking email complete '{email_id}' and '{ticket_id}' ")
        key = f"ticket_{email_id}_{ticket_id}"
        self._storage_repository.remove(key)
