import json

from simple_salesforce import Salesforce, SalesforceGeneralError, SalesforceAuthenticationFailed, SalesforceError
from tenacity import retry, wait_exponential, stop_after_delay, stop_after_attempt, wait_fixed


class CtsClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger
        self._salesforce_sdk = None

    def login(self):
        @retry(stop=stop_after_attempt(self._config.CTS_CONFIG["attempts"]),
               wait=wait_fixed(self._config.CTS_CONFIG["wait_fixed"]),
               reraise=True)
        def login():
            self._logger.info("Logging into CTS...")
            try:
                self._salesforce_sdk = Salesforce(username=self._config.CTS_CONFIG["client_username"],
                                                  password=self._config.CTS_CONFIG["client_password"],
                                                  security_token=self._config.CTS_CONFIG["client_security_token"],
                                                  client_id=self._config.CTS_CONFIG["client_id"],
                                                  domain=self._config.CTS_CONFIG["domain"])
                self._logger.info("Logged into CTS!")
            except SalesforceAuthenticationFailed as sfaf:
                self._logger.error("SalesforceAuthenticationFailed trying to login to CTS")
                self._logger.error(f"{sfaf}")
                raise sfaf
            except SalesforceGeneralError as sfge:
                self._logger.error("SalesforceGeneralError trying to login to CTS")
                self._logger.error(f"{sfge}")
                raise sfge
            except Exception as err:
                self._logger.error("An error occurred while trying to login to CTS")
                self._logger.error(f"{err}")
                raise err
            return True

        try:
            return login()
        except Exception as e:
            return e.args[0]

    def _get_request_headers(self):
        headers = {
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

        return headers

    def create_dispatch(self, payload):
        @retry(wait=wait_exponential(multiplier=self._config.CTS_CONFIG['multiplier'],
                                     min=self._config.CTS_CONFIG['min']),
               stop=stop_after_delay(self._config.CTS_CONFIG['stop_delay']), reraise=True)
        def create_dispatch():
            self._logger.info(f'Creating dispatch...')
            self._logger.info(f'Payload that will be applied : {payload}')
            return_response = dict.fromkeys(["body", "status"])
            try:
                if self._config.CTS_CONFIG['environment'] == 'dev':
                    response = self._salesforce_sdk.Service__c.create(payload, self._get_request_headers())
                elif self._config.CTS_CONFIG['environment'] == 'production':
                    raise Exception("CTS create_dispatch: Not implemented in production.")
                return_response["body"] = dict(response)
                if response["success"] is True:
                    return_response["status"] = 200
                else:
                    return_response["status"] = 400
                return return_response
            except SalesforceError as sfe:
                self._logger.error(f"SFE Error {sfe}")
                return_response["body"] = sfe
                return_response["status"] = 500
                return return_response
        try:
            return create_dispatch()
        except Exception as e:
            return e.args[0]

    def get_dispatch(self, dispatch_number, query_fields):
        @retry(wait=wait_exponential(multiplier=self._config.CTS_CONFIG['multiplier'],
                                     min=self._config.CTS_CONFIG['min']),
               stop=stop_after_delay(self._config.CTS_CONFIG['stop_delay']), reraise=True)
        def get_dispatch():
            self._logger.info(f'Getting dispatch...')
            self._logger.info(f'Getting the dispatch of dispatch id : {dispatch_number}')

            return_response = dict.fromkeys(["body", "status"])
            try:
                where = f" WHERE Name = '{dispatch_number}' "
                query = "SELECT {} FROM Service__c {}".format(query_fields, where)
                self._logger.info(f"Applying query: {query}")
                response = self._salesforce_sdk.query(query)
                # response = self._salesforce_sdk.Service__c.get(dispatch_number)
                self._logger.info(f"Retrieved dispatch: {dispatch_number}")
                return_response["body"] = dict(response)
                return_response["status"] = 200
                return return_response
            except SalesforceError as sfe:
                self._logger.error(f"SFE Error {sfe}")
                return_response["body"] = sfe
                return_response["status"] = 500
                return return_response
        try:
            return get_dispatch()
        except Exception as e:
            return e.args[0]

    def get_all_dispatches(self, query_fields=None):
        @retry(wait=wait_exponential(multiplier=self._config.CTS_CONFIG['multiplier'],
                                     min=self._config.CTS_CONFIG['min']),
               stop=stop_after_delay(self._config.CTS_CONFIG['stop_delay']), reraise=True)
        def get_all_dispatches():
            self._logger.info(f'Getting all dispatches...')

            return_response = dict.fromkeys(["body", "status"])
            try:
                status_clausule = "Status__c in ('Open', 'Scheduled', 'On Site', 'Completed', " \
                                  "'Complete Pending Collateral', 'Canceled')"
                open_date_clausule = "Open_Date__c >= LAST_MONTH"
                where = f" WHERE {status_clausule} and {open_date_clausule}"
                query = "SELECT {} FROM Service__c {}".format(query_fields, where)
                self._logger.info(f"Applying query: {query}")
                response = self._salesforce_sdk.query(query)

                return_response["body"] = dict(response)
                return_response["status"] = 200
                return return_response
            except SalesforceError as sfe:
                self._logger.error(f"SFE Error {sfe}")
                return_response["body"] = sfe
                return_response["status"] = 500
                return return_response
        try:
            return get_all_dispatches()
        except Exception as e:
            return e.args[0]

    def update_dispatch(self, dispatch_id, payload):
        @retry(wait=wait_exponential(multiplier=self._config.CTS_CONFIG['multiplier'],
                                     min=self._config.CTS_CONFIG['min']),
               stop=stop_after_delay(self._config.CTS_CONFIG['stop_delay']), reraise=True)
        def update_dispatch():
            self._logger.info(f'Updating dispatch...')
            self._logger.info(f'Payload that will be applied : {json.dumps(payload, indent=2)}')

            return_response = dict.fromkeys(["body", "status"])
            try:
                if self._config.CTS_CONFIG['environment'] == 'dev':
                    response = self._salesforce_sdk.Service__c.update(dispatch_id, payload,
                                                                      self._get_request_headers())
                elif self._config.CTS_CONFIG['environment'] == 'production':
                    # TODO: Not implemented: send email with specific subject
                    raise Exception("TODO: CTS update_dispatch: Not implemented in production.")
                return_response["body"] = dict(response)
                return_response["status"] = 200
                return return_response
            except SalesforceError as sfe:
                self._logger.error(f"SFE Error {sfe}")
                return_response["body"] = sfe
                return_response["status"] = 500
                return return_response

        try:
            return update_dispatch()
        except Exception as e:
            return e.args[0]
