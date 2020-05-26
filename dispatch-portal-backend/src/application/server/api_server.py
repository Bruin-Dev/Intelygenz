import base64
import time
from http import HTTPStatus
import json
import textwrap
from datetime import datetime
from time import perf_counter

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

from application.mappers import lit_mapper, cts_mapper
from application.templates.dispatch_requested import get_dispatch_requested_note


class DispatchServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, config, redis_client, event_bus, logger):
        self._config = config
        self.MAX_TICKET_NOTE = 1500
        self._one_mega = (1024 * 1024)  # 1mb
        self._max_content_length = 16 * self._one_mega  # 16mb
        self._title = config.DISPATCH_PORTAL_CONFIG['title']
        self._port = config.DISPATCH_PORTAL_CONFIG['port']
        self._hypercorn_config = HyperCornConfig()
        self._new_bind = f'0.0.0.0:{self._port}'
        self._app = Pint(__name__, title=self._title, no_openapi=True,
                         base_model_schema=config.DISPATCH_PORTAL_CONFIG['schema_path'])
        # self._app = cors(self._app, allow_origin="*")
        self._app.config['MAX_CONTENT_LENGTH'] = self._max_content_length
        self.MAIN_WATERMARK = '#*Automation Engine*#'
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
        self._app.add_url_rule("/lit/dispatch", None, self.lit_get_all_dispatches,
                               methods=['GET'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch/<dispatch_number>", None, self.lit_get_dispatch,
                               methods=['GET'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch", None, self.lit_create_dispatch,
                               methods=['POST'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch", None, self.lit_update_dispatch,
                               methods=['PATCH'], strict_slashes=False)
        self._app.add_url_rule("/lit/dispatch/<dispatch_number>/upload-file", None,
                               self.lit_upload_file_to_dispatch, methods=['POST'], strict_slashes=False)

        # self._app.add_url_rule("/cts/dispatch/<dispatch_number>", None, self.cts_get_dispatch,
        #                        methods=['GET'], strict_slashes=False)
        # self._app.add_url_rule("/cts/dispatch", None, self.cts_get_all_dispatches,
        #                        methods=['GET'], strict_slashes=False)
        # self._app.add_url_rule("/cts/dispatch", None, self.cts_create_dispatch,
        #                        methods=['POST'], strict_slashes=False)

    def _health(self):
        return jsonify(None), self._status, None

    # LIT endpoints
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
        response_dispatch['dispatch'] = lit_mapper.map_get_dispatch(response['body']['Dispatch'])

        return jsonify(response_dispatch), response["status"], None

    # Get Dispatch - GET - /lit/dispatch
    async def lit_get_all_dispatches(self):
        self._logger.info(f"--> Getting all dispatches from lit-bridge")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {}}
        response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)
        self._logger.info(response)
        response_dispatch = dict()
        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        if response['status'] not in range(200, 300):
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        if 'body' not in response \
                or 'Status' not in response['body'] \
                or 'DispatchList' not in response['body'] \
                or response['body']['DispatchList'] is None:
            self._logger.error(f"Could not retrieve dispatch, reason: {response['body']}")
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        self._logger.info(f"<-- All Dispatches - {response['body']} - took {time.time() - start_time}")
        response_dispatch['vendor'] = 'LIT'
        response_dispatch['list_dispatch'] = [
            lit_mapper.map_get_dispatch(d) for d in response['body']['DispatchList']]

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
        dispatch_request = lit_mapper.map_create_dispatch(body)
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
            response_dispatch['vendor'] = 'LIT'
            self._logger.info(
                f"Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")

            await self._process_note(dispatch_num, body)
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

        dispatch_request = lit_mapper.map_update_dispatch(body)
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

    # CTS endpoints
    # Get Dispatch - GET - /lit/dispatch/<dispatch_number>
    # async def cts_get_dispatch(self, dispatch_number):
    #     self._logger.info(f"--> Dispatch [{dispatch_number}] from cts-bridge")
    #     start_time = time.time()
    #     payload = {"request_id": uuid(), "body": {"dispatch_number": dispatch_number}}
    #     response = await self._event_bus.rpc_request("cts.dispatch.get", payload, timeout=30)
    #     self._logger.info(response)
    #     response_dispatch = dict()
    #     if response['status'] == 500:
    #         error_response = {
    #             'code': response['status'], 'message': response['body']
    #         }
    #         return jsonify(error_response), response['status'], None
    #     if 'body' not in response or 'Id' not in response['body'] \
    #             or response['body'] is None:
    #         self._logger.error(f"Could not retrieve dispatch, reason: {response['body']}")
    #         error_response = {
    #             'code': response['status'], 'message': response['body']
    #         }
    #         return jsonify(error_response), response['status'], None
    #
    #     self._logger.info(f"<-- Dispatch [{dispatch_number}] - {response['body']} "
    #                       f"- took {time.time() - start_time}")
    #     response_dispatch['id'] = response['body']['Id']
    #     response_dispatch['vendor'] = 'cts'
    #     response_dispatch['dispatch'] = cts_mapper.map_get_dispatch(response['body'])
    #
    #     return jsonify(response_dispatch), response["status"], None

    # Get All Dispatches - GET - /cts/dispatch
    # async def cts_get_all_dispatches(self):
    #     self._logger.info(f"--> Getting all dispatches from cts-bridge")
    #     start_time = time.time()
    #     payload = {"request_id": uuid(), "body": {}}
    #     response = await self._event_bus.rpc_request("cts.dispatch.get", payload, timeout=30)
    #     self._logger.info(response)
    #     response_dispatch = dict()
    #     if response['status'] == 500:
    #         error_response = {
    #             'code': response['status'], 'message': response['body']
    #         }
    #         return jsonify(error_response), response['status'], None
    #
    #     if 'body' not in response \
    #             or 'Status' not in response['body'] \
    #             or 'DispatchList' not in response['body'] \
    #             or response['body']['DispatchList'] is None:
    #         self._logger.error(f"Could not retrieve dispatch, reason: {response['body']}")
    #         error_response = {
    #             'code': response['status'], 'message': response['body']
    #         }
    #         return jsonify(error_response), response['status'], None
    #
    #     self._logger.info(f"<-- All Dispatches - {response['body']} - took {time.time() - start_time}")
    #     response_dispatch['vendor'] = 'cts'
    #     # TODO: check what we retrieve
    #     response_dispatch['list_dispatch'] = [
    #         cts_mapper.map_get_dispatch(d) for d in response['body']['DispatchList']]
    #
    #     return jsonify(response_dispatch), response["status"], None

    # Create Dispatch - POST - /cts/dispatch
    # async def cts_create_dispatch(self):
    #     self._logger.info(f"Creating new dispatch from cts-bridge")
    #     start_time = time.time()
    #     body = await request.get_json()
    #
    #     try:
    #         validate(body, self._schema['components']['schemas']['new_dispatch_cts'])
    #     except jsonschema.exceptions.ValidationError as ve:
    #         self._logger.error(ve)
    #         error_message = "Schema not valid."
    #         self._logger.error(error_message)
    #         error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': ve.message}
    #         return jsonify(error_response), HTTPStatus.BAD_REQUEST, None
    #
    #     self._logger.info(f"payload: {body}")
    #
    #     dispatch_request = cts_mapper.map_create_dispatch(body)
    #
    #     request_body = dict()
    #     request_body['RequestDispatch'] = dispatch_request
    #
    #     payload = {"request_id": uuid(), "body": request_body}
    #     response = await self._event_bus.rpc_request("cts.dispatch.post", payload, timeout=30)
    #     self._logger.info(response)
    #
    #     if response['status'] == 500:
    #         error_response = {
    #             'code': response['status'], 'message': response['body']
    #         }
    #         return jsonify(error_response), response['status'], None
    #
    #     response_dispatch = dict()
    #     if 'body' in response and response['body'] is not None and 'Dispatch' in response['body'] \
    #             and response['body']['Dispatch'] is not None \
    #             and 'Dispatch_Number' in response['body']['Dispatch']:
    #         dispatch_num = response['body']['Dispatch']['Dispatch_Number']
    #         response_dispatch['id'] = dispatch_num
    #         response_dispatch['vendor'] = 'CTS'
    #         self._logger.info(
    #             f"Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")
    #     else:
    #         self._logger.info(f"Dispatch not created - {payload} - took {time.time() - start_time}")
    #         error_response = {'code': response['status'], 'message': response['body']}
    #         return jsonify(error_response), response['status'], None
    #     return jsonify(response_dispatch), HTTPStatus.OK, None

    async def _append_note_to_ticket(self, ticket_id, ticket_note):
        append_note_to_ticket_request = {
            'request_id': uuid(),
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        append_ticket_to_note = await self._event_bus.rpc_request(
            "bruin.ticket.note.append.request", append_note_to_ticket_request, timeout=15
        )
        return append_ticket_to_note

    def _exists_watermark_in_ticket(self, watermark, ticket_notes):
        watermark_found = False

        for ticket_note_data in ticket_notes:
            self._logger.info(ticket_note_data)
            ticket_note = ticket_note_data.get('noteValue')

            if self.MAIN_WATERMARK in ticket_note and watermark in ticket_note:
                watermark_found = True
                break

        return watermark_found

    async def _get_ticket_details(self, ticket_id):
        ticket_request_msg = {'request_id': uuid(),
                              'body': {'ticket_id': ticket_id}}
        ticket = await self._event_bus.rpc_request("bruin.ticket.details.request", ticket_request_msg, timeout=200)
        return ticket

    async def _process_note(self, dispatch_number, body):
        try:
            ticket_id = body['mettel_bruin_ticket_id']
            ticket_note = get_dispatch_requested_note(body, dispatch_number)

            # Split the note if needed
            ticket_notes = textwrap.wrap(ticket_note, self.MAX_TICKET_NOTE, replace_whitespace=False)

            pre_existing_ticket_notes_response = await self._get_ticket_details(ticket_id)
            pre_existing_ticket_notes_status = pre_existing_ticket_notes_response['status']

            if pre_existing_ticket_notes_status not in range(200, 300):
                self._logger.error(f"Error: could not retrieve ticket [{ticket_id}] details")
                return

            pre_existing_ticket_notes_body = pre_existing_ticket_notes_response.get('body', {})
            pre_existing_ticket_notes = pre_existing_ticket_notes_body.get('ticketNotes', [])
            watermark_found = self._exists_watermark_in_ticket('Dispatch Management - Dispatch Requested',
                                                               pre_existing_ticket_notes)
            if watermark_found is True:
                # TODO: decide what to do
                self._logger.info(f"Not adding note for dispatch [{dispatch_number}] to ticket {ticket_id}")
            else:
                for i, note in enumerate(ticket_notes):
                    self._logger.info(f"Appending note_{i} to ticket {ticket_id}")
                    append_note_response = await self._append_note_to_ticket(body['mettel_bruin_ticket_id'], note)
                    append_note_response_status = append_note_response['status']
                    append_note_response_body = append_note_response['body']
                    if append_note_response_status not in range(200, 300):
                        self._logger.error(f"[process_note] Error appending note: `{note}` "
                                           f"Dispatch: {dispatch_number} "
                                           f"Ticket_id: {body['mettel_bruin_ticket_id']} - Not appended")
                        continue
                    self._logger.info(f"[process_note] Note: `{note}` Dispatch: {dispatch_number} "
                                      f"Ticket_id: {body['mettel_bruin_ticket_id']} - Appended")
                    self._logger.info(f"[process_note] Note appended. Response {append_note_response_body}")
        except Exception as ex:
            self._logger.error(f"[process_note] Error: {ex}")
