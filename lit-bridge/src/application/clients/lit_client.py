import json

from simple_salesforce import Salesforce, SalesforceGeneralError, SalesforceAuthenticationFailed, SalesforceError
from tenacity import retry, wait_exponential, stop_after_delay, stop_after_attempt, wait_fixed


class LitClient:
    def __init__(self, logger, config):
        self._config = config
        self._logger = logger
        self._salesforce_sdk = None

    def login(self):
        @retry(stop=stop_after_attempt(self._config.LIT_CONFIG["attempts"]),
               wait=wait_fixed(self._config.LIT_CONFIG["wait_fixed"]),
               reraise=True)
        def login():
            self._logger.info("Logging into Lit...")
            try:
                self._salesforce_sdk = Salesforce(username=self._config.LIT_CONFIG["client_username"],
                                                  password=self._config.LIT_CONFIG["client_password"],
                                                  security_token=self._config.LIT_CONFIG["client_security_token"],
                                                  client_id=self._config.LIT_CONFIG["client_id"],
                                                  domain=self._config.LIT_CONFIG["domain"])
                self._logger.info("Logged into Lit!")
            except SalesforceAuthenticationFailed as sfaf:
                self._logger.error("SalesforceAuthenticationFailed trying to login to Lit")
                self._logger.error(f"{sfaf}")
                raise sfaf
            except SalesforceGeneralError as sfge:
                self._logger.error("SalesforceGeneralError trying to login to Lit")
                self._logger.error(f"{sfge}")
                raise sfge
            except Exception as err:
                self._logger.error("An error occurred while trying to login to Lit")
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
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def create_dispatch():
            self._logger.info(f'Creating dispatch...')
            self._logger.info(f'Payload that will be applied : {payload}')
            return_response = dict.fromkeys(["body", "status"])

            try:
                response = self._salesforce_sdk.apexecute('NewDispatch', method='POST',
                                                          headers=self._get_request_headers(),
                                                          data=payload,
                                                          verify=False)
                return_response["body"] = response
                if response["Status"] == "Success":
                    return_response["status"] = 200
                if response["Status"] == "error":
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

    def get_dispatch(self, dispatch_number):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def get_dispatch():
            self._logger.info(f'Getting dispatch...')
            self._logger.info(f'Getting the dispatch of dispatch number : {dispatch_number}')

            return_response = dict.fromkeys(["body", "status"])
            try:
                response = self._salesforce_sdk.apexecute(f'GetDispatch/{dispatch_number}', method='GET',
                                                          headers=self._get_request_headers(),
                                                          verify=False)
                return_response["body"] = response
                if response["Status"] == "Success":
                    return_response["status"] = 200
                if response["Status"] == "error":
                    return_response["status"] = 400
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

    def get_all_dispatches(self):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def get_all_dispatches():
            self._logger.info(f'Getting all dispatches...')

            return_response = dict.fromkeys(["body", "status"])
            try:
                response = self._salesforce_sdk.apexecute('GetOpenDispatchList', method='GET',
                                                          headers=self._get_request_headers(),
                                                          verify=False)
                return_response["body"] = response
                if response["Status"] == "Success":
                    return_response["status"] = 200
                if response["Status"] == "error":
                    return_response["status"] = 400
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

    def update_dispatch(self, payload):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def update_dispatch():
            self._logger.info(f'Updating dispatch...')
            self._logger.info(f'Payload that will be applied : {json.dumps(payload, indent=2)}')

            return_response = dict.fromkeys(["body", "status"])
            try:
                response = self._salesforce_sdk.apexecute('UpdateDispatch', method='POST',
                                                          data=payload,
                                                          headers=self._get_request_headers(),
                                                          verify=False)
                return_response["body"] = response
                if response["Status"] == "Success":
                    return_response["status"] = 200
                if response["Status"] == "error":
                    return_response["status"] = 400
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

    def upload_file(self, dispatch_id, payload, file_name, file_content_type="application/octet-stream"):
        @retry(wait=wait_exponential(multiplier=self._config.LIT_CONFIG['multiplier'],
                                     min=self._config.LIT_CONFIG['min']),
               stop=stop_after_delay(self._config.LIT_CONFIG['stop_delay']), reraise=True)
        def upload_file():
            self._logger.info(f'Upload file to dispatch dispatch...')
            self._logger.info(f'Payload that will be applied : {len(payload)}')

            headers = self._get_request_headers()

            # Udpate headers with file_content_type
            headers["Content-Type"] = file_content_type
            # Mandatory field
            headers["filename"] = file_name

            # TODO: check if the backend send it to me already in the proper format
            # raw_data = base64.b64encode(payload).decode('utf-8')
            raw_data = payload

            return_response = dict.fromkeys(["body", "status"])
            try:
                response = self._salesforce_sdk.apexecute(f'UploadDispatchFile/{dispatch_id}', method='POST',
                                                          data=raw_data, verify=False, headers=headers)
                return_response["body"] = response

                if response["Status"] == "Success":
                    return_response["status"] = 200
                if response["Status"] == "error":
                    return_response["status"] = 400
                return return_response
            except SalesforceError as sfe:
                self._logger.error(f"SFE Error {sfe}")
                return_response["body"] = sfe
                return_response["status"] = 500
                return return_response

        try:
            return upload_file()
        except Exception as e:
            return e.args[0]
