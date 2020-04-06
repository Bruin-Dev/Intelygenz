import base64
import time
from http import HTTPStatus
import json

import jsonschema
from jsonschema import validate
from quart import jsonify, request
from quart_cors import cors
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from quart.exceptions import HTTPException
from quart_openapi import Pint
from shortuuid import uuid
from swagger_ui import quart_api_doc

from application.mappers.lit_mapper import map_get_dispatch, map_create_dispatch, map_update_dispatch


class DispatchServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, config, redis_client, event_bus, logger):
        self._config = config
        self._one_mega = (1024 * 1024)  # 1mb
        self._max_content_length = 16 * self._one_mega  # 16mb
        self._title = config.DISPATCH_PORTAL_CONFIG['title']
        self._port = config.DISPATCH_PORTAL_CONFIG['port']
        self._hypercorn_config = HyperCornConfig()
        self._new_bind = f'0.0.0.0:{self._port}'
        self._app = Pint(__name__, title=self._title, no_openapi=True,
                         base_model_schema=config.DISPATCH_PORTAL_CONFIG['schema_path'])
        self._app = cors(self._app, allow_origin="*")
        self._app.config['MAX_CONTENT_LENGTH'] = self._max_content_length
        self._redis_client = redis_client
        self._event_bus = event_bus
        self._logger = logger
        self._status = HTTPStatus.OK
        self.attach_swagger()
        self.register_endpoints()
        with open(config.DISPATCH_PORTAL_CONFIG['schema_path'], 'r') as f:
            schema_data = f.read()
        self._schema = json.loads(schema_data)
        self._create_dispatch_schema = self._app.create_ref_validator('new_dispatch_lit', 'schemas')

    async def run_server(self):
        self._hypercorn_config.bind = [self._new_bind]
        await serve(self._app, self._hypercorn_config)

    def attach_swagger(self):
        quart_api_doc(self._app, editor=True,
                      config_path=self._config.DISPATCH_PORTAL_CONFIG['swagger_path'],
                      url_prefix=self._config.DISPATCH_PORTAL_CONFIG['swagger_url_prefix'],
                      title=self._config.DISPATCH_PORTAL_CONFIG['swagger_title'])

    def set_status(self, new_status):
        self._status = new_status

    def register_endpoints(self):
        self._app.add_url_rule("/_health", None, self._health)
        self._app.add_url_rule("/lit/dispatch/<dispatch_number>", None, self.lit_get_dispatch,
                               methods=['GET'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch", None, self.lit_create_dispatch,
                               methods=['POST'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch", None, self.lit_update_dispatch,
                               methods=['PATCH'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch/<dispatch_number>/upload-file", None,
                               self.lit_upload_file_to_dispatch, methods=['POST'], strict_slashes=False)

    def _health(self):
        return jsonify(None), self._status, None

    # LIT Endpoints
    # Get Dispatch - GET - /lit/dispatch/<dispatch_number>
    async def lit_get_dispatch(self, dispatch_number):
        self._logger.info(f"--> Dispatch [{dispatch_number}] from lit-bridge")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {"dispatch_number": dispatch_number}}
        response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)
        self._logger.info(response)
        response_dispatch = dict()
        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None
        if 'body' not in response or 'Dispatch' not in response['body'] \
                or response['body']['Dispatch'] is None \
                or 'Dispatch_Number' not in response['body']['Dispatch']:
            self._logger.error(f"Could not retrieve dispatch, reason: {response['body']}")
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        self._logger.info(f"<-- Dispatch [{dispatch_number}] - {response['body']} "
                          f"- took {time.time() - start_time}")
        response_dispatch['id'] = response['body']['Dispatch']['Dispatch_Number']
        response_dispatch['vendor'] = 'lit'
        response_dispatch['dispatch'] = map_get_dispatch(response['body']['Dispatch'])

        return jsonify(response_dispatch), response["status"], None

    # Create Dispatch - POST - /lit/dispatch
    async def lit_create_dispatch(self):
        self._logger.info(f"Creating new dispatch from lit-bridge")
        start_time = time.time()
        body = await request.get_json()

        try:
            validate(body, self._schema['components']['schemas']['new_dispatch_lit'])
        except jsonschema.exceptions.ValidationError as ve:
            self._logger.error(ve)
            error_message = "Schema not valid."
            self._logger.error(error_message)
            error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': ve.message}
            return jsonify(error_response), HTTPStatus.BAD_REQUEST, None

        self._logger.info(f"payload: {body}")

        dispatch_request = map_create_dispatch(body)

        request_body = dict()
        request_body['RequestDispatch'] = dispatch_request

        payload = {"request_id": uuid(), "body": request_body}
        response = await self._event_bus.rpc_request("lit.dispatch.post", payload, timeout=30)
        self._logger.info(response)

        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        response_dispatch = dict()
        if 'body' in response and response['body'] is not None and 'Dispatch' in response['body'] \
                and response['body']['Dispatch'] is not None \
                and 'Dispatch_Number' in response['body']['Dispatch']:
            dispatch_num = response['body']['Dispatch']['Dispatch_Number']
            response_dispatch['id'] = dispatch_num
            response_dispatch['vendor'] = 'lit'
            self._logger.info(
                f"Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")
        else:
            self._logger.info(f"Dispatch not created - {payload} - took {time.time() - start_time}")
            error_response = {'code': response['status'], 'message': response['body']}
            return jsonify(error_response), response['status'], None
        return jsonify(response_dispatch), HTTPStatus.OK, None

    # Update Dispatch - PATCH - /lit/dispatch
    async def lit_update_dispatch(self):
        start_time = time.time()
        body = await request.get_json()
        try:
            validate(body, self._schema['components']['schemas']['update_dispatch_lit'])
        except jsonschema.exceptions.ValidationError as ve:
            self._logger.error(ve)
            error_message = "Schema not valid."
            self._logger.error(error_message)
            error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': ve.message}
            return jsonify(error_response), HTTPStatus.BAD_REQUEST, None

        dispatch_request = map_update_dispatch(body)
        dispatch_number = body['dispatch_number']

        request_body = dict()
        request_body['RequestDispatch'] = dispatch_request

        self._logger.info(f"Updating dispatch [{dispatch_number}] from lit-bridge")
        self._logger.info(f"payload: {body}")

        payload = {"request_id": uuid(), "body": request_body}
        response = await self._event_bus.rpc_request("lit.dispatch.update", payload, timeout=30)
        self._logger.info(response)
        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        response_dispatch = dict()

        if 'body' in response and response['body'] is not None and 'Dispatch' in response['body'] \
                and response['body']['Dispatch'] \
                and 'Dispatch_Number' in response['body']['Dispatch']:
            dispatch_num = response['body']['Dispatch']['Dispatch_Number']
            response_dispatch['id'] = dispatch_num
            response_dispatch['vendor'] = 'lit'
            self._logger.info(
                f"Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")
        else:
            self._logger.info(f"Dispatch not updated - {payload} - took {time.time() - start_time}")
            error_response = {'code': response['status'], 'message': response['body']}
            return jsonify(error_response), response['status'], None
        return jsonify(response_dispatch), HTTPStatus.OK, None

    # Upload File to Dispatch - POST - /lit/dispatch/<dispatch_number>/upload-file
    async def lit_upload_file_to_dispatch(self, dispatch_number):
        try:
            start_time = time.time()
            self._logger.info(f"Uploading file to dispatch [{dispatch_number}] from lit-bridge")
            content_length = request.headers.get('content-length', None)
            self._logger.info(f"File content length -- {content_length}")
            if content_length is not None and int(content_length) > self._max_content_length:
                raise HTTPException(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Entity too large", "http_exception")
            file_name = request.headers.get('filename', None)
            if file_name is None:
                error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': 'No `filename` in headers'}
                return jsonify(error_response), HTTPStatus.BAD_REQUEST, None
            content_type = request.headers.get('content-type', None)
            if content_type is None or content_type != 'application/octet-stream':
                error_response = {
                    'code': HTTPStatus.BAD_REQUEST,
                    'message': '`content-type` in headers not present or different to `application/octet-stream`'
                }
                return jsonify(error_response), HTTPStatus.BAD_REQUEST, None

            body = await request.get_data(raw=True)
            if len(body) == 0:
                error_message = "Body provided is empty"
                self._logger.error(error_message)
                error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': error_message}
                return jsonify(error_response), HTTPStatus.BAD_REQUEST, None
            body = base64.b64encode(body).decode('utf-8')
            payload_body = {
                'dispatch_number': dispatch_number,
                'payload': body,
                'file_name': file_name
            }
            payload = {"request_id": uuid(), "body": payload_body}
            response = await self._event_bus.rpc_request("lit.dispatch.upload.file", payload, timeout=300)
            self._logger.info(response)
            if response['status'] == 500:
                error_response = {
                    'code': response['status'], 'message': response['body']
                }
                return jsonify(error_response), response['status'], None

            response_dispatch = dict()
            if response['status'] in range(200, 300):
                self._logger.info(f"Uploaded Dispatch File [{dispatch_number}] "
                                  f"- {len(body)} bytes - took {time.time() - start_time}")
                response_dispatch['id'] = dispatch_number
                response_dispatch['vendor'] = 'lit'
                response_dispatch['file_id'] = response['body']['Message'].split(':')[1]
            else:
                self._logger.error(f"Error Upload Dispatch File: {response['body']}")
                error_response = {'code': response['status'], 'message': response['body']}
                return jsonify(error_response), response['status'], None
            return jsonify(response_dispatch), HTTPStatus.OK, None
        except Exception as ex:
            self._logger.error("ERROR")
            self._logger.error(ex)
            error_response = {'code': ex.status_code, 'message': ex.description}
            return jsonify(error_response), ex.status_code
