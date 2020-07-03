class CreateDispatch:

    def __init__(self, logger, config, event_bus, cts_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._cts_repository = cts_repository

    async def create_dispatch(self, msg):
        create_dispatch_response = {
            "request_id": msg["request_id"],
            "body": None,
            "status": None
        }

        if msg.get("body") is None:
            create_dispatch_response["status"] = 400
            create_dispatch_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], create_dispatch_response)
            return
        request_dispatch_payload = msg["body"]

        dispatch_required_keys = ['date_of_dispatch', 'site_survey_quote_required', 'time_of_dispatch', 'time_zone',
                                  'mettel_bruin_ticket_id', 'sla_level', 'location_country', 'job_site',
                                  'job_site_street_1', 'job_site_city', 'job_site_state',
                                  'job_site_zip_code', 'job_site_contact_name', 'job_site_contact_lastname',
                                  'job_site_contact_number', 'materials_needed_for_dispatch', 'scope_of_work',
                                  'mettel_tech_call_in_instructions', 'service_type', 'name_of_mettel_requester',
                                  'lastname_of_mettel_requester', 'mettel_department', 'mettel_requester_email',
                                  'mettel_department_phone_number']

        # request_dispatch_payload = {k.lower(): v for k, v in request_dispatch_payload.items()}
        if all(key in request_dispatch_payload.keys() for key in dispatch_required_keys):
            self._logger.info('Creating a new dispatch')
            request_dispatch = self._cts_repository.create_dispatch(msg["body"])

            if request_dispatch["status"] in range(200, 300):
                self._logger.info(f'Created a dispatch with dispatch number: '
                                  f'{request_dispatch["body"]}')
            else:
                self._logger.info(f'Not created a dispatch with payload: {msg["body"]}')

            create_dispatch_response["body"] = request_dispatch["body"]
            create_dispatch_response["status"] = request_dispatch["status"]
        else:
            create_dispatch_response["status"] = 400
            create_dispatch_response["body"] = f'Must include the following keys in request: {dispatch_required_keys}'
        await self._event_bus.publish_message(msg['response_topic'], create_dispatch_response)
