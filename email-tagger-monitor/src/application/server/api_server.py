import hmac
import hashlib
import os
import re
import json
import time
from http import HTTPStatus

import jsonschema
from functools import wraps
from typing import List

from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from jsonschema import validate
from quart import jsonify, request
from quart_openapi import Pint
from swagger_ui import quart_api_doc

MEGABYTE: int = (1024 * 1024)
MAX_CONTENT_LENGTH = 4 * MEGABYTE  # 4mb
SHA256_PREFIX = re.compile(r"^sha256=")


class APIServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, logger, config, new_emails_repository, new_tickets_repository, notifications_repository,
                 utils_repository):
        self._config = config
        self._logger = logger
        self._new_emails_repository = new_emails_repository
        self._new_tickets_repository = new_tickets_repository
        self._notifications_repository = notifications_repository
        self._utils = utils_repository

        self._max_content_length = MAX_CONTENT_LENGTH
        self._title = config.QUART_CONFIG['title']
        self._port = config.QUART_CONFIG['port']
        self._use_request_api_key_header = config.MONITOR_CONFIG['api_server']['use_request_api_key_header']

        self._endpoint_prefix = config.MONITOR_CONFIG['api_server']['endpoint_prefix']

        self._hypercorn_config = HyperCornConfig()

        self._logger.info(f'env: {os.environ}')
        self._new_bind = f'0.0.0.0:{self._port}'
        self._app = Pint(__name__, title=self._title, no_openapi=True,
                         base_model_schema=config.MONITOR_CONFIG['api_server']['schema_path'])

        self.attach_swagger()
        self.register_endpoints()
        with open(config.MONITOR_CONFIG['api_server']['schema_path'], 'r') as f:
            schema_data = f.read()
        self._schema = json.loads(schema_data)
        self._create_schema = self._app.create_ref_validator('new_email_tagger_validator', 'schemas')

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        await serve(self._app, self._hypercorn_config)

    def attach_swagger(self):
        quart_api_doc(self._app, editor=True,
                      config_path=self._config.MONITOR_CONFIG['api_server']['swagger_path'],
                      url_prefix=self._config.MONITOR_CONFIG['api_server']['swagger_url_prefix'],
                      title=self._config.MONITOR_CONFIG['api_server']['swagger_title'])

    def register_endpoints(self):
        self._app.add_url_rule("/_health", None, self._health)
        self._app.add_url_rule(self._endpoint_prefix + "/email", None, self._post_email, methods=['POST'],
                               strict_slashes=False)
        self._app.add_url_rule(self._endpoint_prefix + "/ticket", None, self._post_ticket, methods=['POST'],
                               strict_slashes=False)

    # Middleware decorators

    def validate_api_key(func):
        @wraps(func)
        async def decorated(_self):
            if not _self._use_request_api_key_header:
                return await func(_self)

            api_key = request.headers.get("api-key")

            if not api_key:
                err_msg = f"Missing api-key header"
                _self._logger.error(err_msg)
                return_response = {
                    "code": "MissingAPIKey",
                    "message": err_msg
                }
                return jsonify(return_response), HTTPStatus.BAD_REQUEST, None

            valid = _self._is_valid_api_key(api_key)
            if not valid:
                err_msg = f"Invalid api-key header"
                _self._logger.error(err_msg)
                return_response = {
                    "code": "InvalidAPIKeyHeader",
                    "message": err_msg
                }
                return jsonify(return_response), HTTPStatus.BAD_REQUEST, None

            return await func(_self)

        return decorated

    def verify_signature(func):
        @wraps(func)
        async def decorated(_self):
            header_signature = request.headers.get("x-bruin-webhook-signature")
            if header_signature is None:
                err_response = {
                    "code": "MissingSignature",
                    "message": "Signature header 'x-bruin-webhook-signature' missing."
                }
                return jsonify(err_response), HTTPStatus.BAD_REQUEST, None

            body = await request.get_data()
            valid = _self._is_valid_signature(body, header_signature)
            if not valid:
                err_msg = f"Invalid body signature"
                _self._logger.error(err_msg)
                return_response = {
                    "code": "InvalidSignature",
                    "message": err_msg
                }

                return jsonify(return_response), HTTPStatus.BAD_REQUEST, None

            return await func(_self)

        return decorated

    def _is_valid_api_key(self, api_key: str) -> bool:
        return api_key == self._config.MONITOR_CONFIG['api_server']['request_api_key']

    def _is_valid_signature(self, content: str, signature_to_verify: str) -> bool:
        secret_key = bytes(self._config.MONITOR_CONFIG['api_server']['request_signature_secret_key'], 'utf-8')
        calculated_signature = hmac.new(secret_key, content, hashlib.sha256).hexdigest()
        calculated_signature = calculated_signature.upper()
        # to upper and remove prefix
        signature_to_verify = SHA256_PREFIX.sub("", signature_to_verify)
        signature_to_verify = signature_to_verify.upper()

        self._logger.info(f"Request RAW body: \n>>>>{content}<<<<<<\n")
        self._logger.info(f"Signature: IGZ  [{calculated_signature}]")
        self._logger.info(f"Signature: BRUIN[{signature_to_verify}]")

        # Use try/except because compare_digest may be disabled
        try:
            return hmac.compare_digest(calculated_signature, signature_to_verify)
        except AttributeError:
            return calculated_signature == signature_to_verify

    # Endpoints
    def _health(self):
        return jsonify(None), HTTPStatus.OK, None

    @validate_api_key
    @verify_signature
    # New Email Notification [POST] /email
    async def _post_email(self):
        self._logger.info(f"[EmailWebhook] new email received")
        start_time = time.time()

        notification_data = await request.get_json()
        email_data = notification_data.get('Notification', {}).get('Body')

        try:
            validate(email_data, self._schema['components']['schemas'])
        except jsonschema.exceptions.ValidationError as ve:
            self._logger.error(ve)
            error_message = "email data not valid."
            self._logger.error(error_message)
            error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': ve.message}
            return jsonify(error_response), HTTPStatus.BAD_REQUEST, None

        try:
            self._new_emails_repository.save_new_email(self._convert_email_input_body(email_data))
        except Exception as e:
            self._logger.error(f"Error saving new email: {e}")
            error_response = {
                'code': 'InternalServerError',
                'message': "Error saving new email."
            }
            return jsonify(error_response), HTTPStatus.INTERNAL_SERVER_ERROR, None

        self._logger.info("[EmailWebhook] Saved - took {:.3f}s".format(time.time() - start_time))
        return "", HTTPStatus.NO_CONTENT, None

    @validate_api_key
    @verify_signature
    # New Ticket for Email Notification [POST] /ticket
    async def _post_ticket(self):
        self._logger.info(f"[EmailWebhook] new ticket received")
        start_time = time.time()

        notification_data = await request.get_json()
        email_ticket_data = notification_data.get('Notification', {}).get('Body')

        try:
            validate(email_ticket_data, self._schema['components']['schemas'])
        except jsonschema.exceptions.ValidationError as ve:
            self._logger.error(ve)
            error_message = "email ticket data not valid."
            self._logger.error(error_message)
            error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': ve.message}
            return jsonify(error_response), HTTPStatus.BAD_REQUEST, None

        self._logger.info(f"[EmailWebhook] payload: {email_ticket_data}")

        try:
            data = self._convert_ticket_input_body(email_ticket_data)
            email_data = data["original_email"]
            ticket_data = data["ticket"]
            self._new_tickets_repository.save_new_ticket(email_data, ticket_data)
        except Exception as e:
            self._logger.error(f"Error saving new ticket: {e}")
            error_response = {
                'code': 'InternalServerError',
                'message': "Error saving new email."
            }
            return jsonify(error_response), HTTPStatus.INTERNAL_SERVER_ERROR, None

        self._logger.info("[TicketWebhook] Saved - took {:.3f}s".format(time.time() - start_time))

        return "", HTTPStatus.NO_CONTENT, None

    def _convert_email_input_body(self, data: dict) -> dict:
        formatted = self._utils.convert_dict_to_snake_case(data)
        formatted = self._convert_to_str(formatted, ['email_id', 'client_id', 'parent_id', 'previous_email_id'])

        tag_ids = formatted.pop('tag_id', None)

        if tag_ids is not None and not isinstance(tag_ids, list):
            tag_ids = [tag_ids]

        data = {
            'email': formatted,
            'tag_ids': tag_ids
        }

        return data

    def _convert_ticket_input_body(self, data: dict) -> dict:
        email = self._utils.convert_dict_to_snake_case(data)
        ticket = email.pop('ticket')
        email = self._convert_to_str(email, ['email_id', 'client_id', 'parent_id', 'previous_email_id'])
        ticket = self._convert_to_str(ticket, ['ticket_id'])

        tag_ids = email.pop('tag_id', None)

        return {
            'original_email': {
                'email': email,
                'tag_ids': tag_ids
            },
            'ticket': ticket
        }

    def _convert_to_str(self, data: dict, keys: List[str]) -> dict:
        data_keys = data.keys()
        for k in keys:
            if k in data_keys:
                data[k] = str(data[k])

        return data
