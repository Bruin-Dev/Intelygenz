
class CtsRepository:
    def __init__(self, logger, config, event_bus, notifications_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository

    def update_body_with_client_address(self, body, ticket_address_response):
        body['job_site'] = ticket_address_response['clientName']
        body['job_site_street_1'] = ticket_address_response['address']['address']
        body['job_site_city'] = ticket_address_response['address']['city']
        body['job_site_state'] = ticket_address_response['address']['state']
        body['job_site_zip_code'] = ticket_address_response['address']['zip']
        body['location_country'] = ticket_address_response['address']['country']
        return body
