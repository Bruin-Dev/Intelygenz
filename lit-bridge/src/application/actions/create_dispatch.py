class CreateDispatch:

    def __init__(self, logger, config, event_bus, lit_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._lit_repository = lit_repository

    async def create_dispatch(self, msg):
        create_dispatch_response = {"request_id": msg["request_id"], "body": None,
                                    "status": None}

        if msg.get("body") is None:
            create_dispatch_response["status"] = 400
            create_dispatch_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], create_dispatch_response)
            return
        request_dispatch_payload = msg["body"].get("RequestDispatch")
        if request_dispatch_payload is None:
            create_dispatch_response["status"] = 400
            create_dispatch_response["body"] = 'Must include "RequestDispatch" in request'
            await self._event_bus.publish_message(msg['response_topic'], create_dispatch_response)
            return

        dispatch_required_keys = ["date_of_dispatch", "site_survey_quote_required", "local_time_of_dispatch",
                                  "time_zone_local", "job_site", "job_site_street", "job_site_city",
                                  "job_site_state", "job_site_zip_code", "job_site_contact_name_and_phone_number",
                                  "special_materials_needed_for_dispatch", "scope_of_work",
                                  "mettel_tech_call_in_instructions", "name_of_mettel_requester", "mettel_department",
                                  "mettel_requester_email"]

        request_dispatch_payload = {k.lower(): v for k, v in request_dispatch_payload.items()}

        if all(key in request_dispatch_payload.keys() for key in dispatch_required_keys):
            self._logger.info('Creating a new dispatch')
            request_dispatch = self._lit_repository.create_dispatch(msg["body"])

            if request_dispatch["status"] in range(200, 300):
                self._logger.info(f'Created a dispatch with dispatch number: '
                                  f'{request_dispatch["body"]["Dispatch"]["Dispatch_Number"]}')

            create_dispatch_response["body"] = request_dispatch["body"]
            create_dispatch_response["status"] = request_dispatch["status"]
        else:
            create_dispatch_response["status"] = 400
            create_dispatch_response["body"] = f'Must include the following keys in request: {dispatch_required_keys}'
        await self._event_bus.publish_message(msg['response_topic'], create_dispatch_response)
