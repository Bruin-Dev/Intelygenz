from shortuuid import uuid

from phonenumbers import NumberParseException
import phonenumbers

from application.repositories import nats_error_response


class CtsRepository:
    def __init__(self, logger, config, event_bus, notifications_repository, redis_client):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository
        self._redis_client = redis_client

    async def get_all_dispatches(self):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {},
        }

        try:
            self._logger.info(f'Getting all dispatches from CTS...')
            response = await self._event_bus.rpc_request("cts.dispatch.get", request, timeout=30)
            self._logger.info(f'Got all dispatches from CTS!')
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting all dispatches from CTS -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving all tickets from CTS in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    @staticmethod
    def is_valid_ticket_id(ticket_id):
        # Check ticket id format for example: '4663397|IW24654081'
        # Bruin ticket ID like 712637/IW76236 and 123-3123 are likely to be from other
        # kind of tickets (like new installations), thus other teams that are not his,
        # 4485610(Order)/4520284(Port)
        # Discard All with more than one ticket
        ticket_id = ticket_id.replace(' ', '')
        ticket_id_1 = ticket_id.split('|')
        ticket_id_2 = ticket_id.split('-')
        ticket_id_3 = ticket_id.split('/')
        if len(ticket_id_1) > 1:
            return False
        elif len(ticket_id_2) > 1:
            return False
        elif len(ticket_id_3) > 1:
            return False
        return True

    @staticmethod
    def get_sms_to(dispatch):
        description = dispatch.get('Description__c')
        description_lines = description.splitlines()
        # Find sms to number
        sms_to = None
        for line in description_lines:
            if line and len(line) > 0 and 'Contact #:' in line:
                sms_to = ''.join(ch for ch in line if ch.isdigit())
                break
        if sms_to is None or sms_to.strip() == '':
            return None
        try:
            # TODO: check other countries
            sms_to = phonenumbers.parse(sms_to, "US")
            return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            return None

    @staticmethod
    def get_sms_to_tech(dispatch):
        # Example format->  Resource_Phone_Number__c: "+1 666 6666 666"
        sms_to = dispatch.get('Resource_Phone_Number__c')
        if sms_to is None or sms_to.strip() == '':
            return None
        # Remove non digits
        sms_to = ''.join(ch for ch in sms_to if ch.isdigit())
        try:
            sms_to = phonenumbers.parse(sms_to, "US")
            return phonenumbers.format_number(sms_to, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            return None
