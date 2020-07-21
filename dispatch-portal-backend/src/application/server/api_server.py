import base64
import json
import textwrap
import time
from http import HTTPStatus

import jsonschema
from application.mappers import lit_mapper, cts_mapper
from application.templates.cts.dispatch_request_mail import render_email_template
from application.templates.cts.dispatch_requested import get_dispatch_requested_note as cts_get_dispatch_requested_note
from application.templates.lit.dispatch_requested import get_dispatch_requested_note as lit_get_dispatch_requested_note
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from jsonschema import validate
from quart import jsonify, request
from quart.exceptions import HTTPException
from quart_openapi import Pint
from shortuuid import uuid
from swagger_ui import quart_api_doc


class DispatchServer:
    _title = None
    _port = None
    _hypercorn_config = None
    _new_bind = None

    def __init__(self, config, redis_client, event_bus, logger, bruin_repository, notifications_repository):
        self._config = config
        self._redis_client = redis_client
        self._event_bus = event_bus
        self._logger = logger
        self._status = HTTPStatus.OK
        self.MAIN_WATERMARK = '#*Automation Engine*#'
        self.DISPATCH_REQUESTED_WATERMARK = 'Dispatch Management - Dispatch Requested'
        self.PENDING_DISPATCHES_KEY = 'pending_dispatches'
        self.MAX_TICKET_NOTE = 1500
        self._one_mega = (1024 * 1024)  # 1mb
        self._max_content_length = 16 * self._one_mega  # 16mb
        self._title = config.DISPATCH_PORTAL_CONFIG['title']
        self._port = config.DISPATCH_PORTAL_CONFIG['port']
        self._hypercorn_config = HyperCornConfig()
        # self._hypercorn_config.debug = True
        # self._hypercorn_config.error_logger = self._logger
        self._new_bind = f'0.0.0.0:{self._port}'
        self._app = Pint(__name__, title=self._title, no_openapi=True,
                         base_model_schema=config.DISPATCH_PORTAL_CONFIG['schema_path'])
        # self._app = cors(self._app, allow_origin="*")
        self._app.config['MAX_CONTENT_LENGTH'] = self._max_content_length
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository
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

        self._app.add_url_rule("/cts/dispatch/<dispatch_number>", None, self.cts_get_dispatch,
                               methods=['GET'], strict_slashes=False)
        self._app.add_url_rule("/cts/dispatch", None, self.cts_get_all_dispatches,
                               methods=['GET'], strict_slashes=False)
        self._app.add_url_rule("/cts/dispatch", None, self.cts_create_dispatch,
                               methods=['POST'], strict_slashes=False)

    def _health(self):
        return jsonify(None), self._status, None

    # LIT endpoints
    # Get Dispatch - GET - /lit/dispatch/<dispatch_number>
    async def lit_get_dispatch(self, dispatch_number):
        self._logger.info(f"[LIT] Dispatch [{dispatch_number}] from lit-bridge")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {"dispatch_number": dispatch_number}}
        response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)
        self._logger.info(f"[LIT] Get dispatch [{dispatch_number}]: {response}")
        response_dispatch = dict()
        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None
        if 'body' not in response or 'Dispatch' not in response['body'] \
                or response['body']['Dispatch'] is None \
                or 'Dispatch_Number' not in response['body']['Dispatch']:
            self._logger.error(f"[LIT] Could not retrieve dispatch, reason: {response['body']}")
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        self._logger.info(f"[LIT] Dispatch [{dispatch_number}] - {response['body']} "
                          f"- took {time.time() - start_time}")
        response_dispatch['id'] = response['body']['Dispatch']['Dispatch_Number']
        response_dispatch['vendor'] = 'lit'
        response_dispatch['dispatch'] = lit_mapper.map_get_dispatch(response['body']['Dispatch'])

        return jsonify(response_dispatch), response["status"], None

    # Get Dispatch - GET - /lit/dispatch
    async def lit_get_all_dispatches(self):
        self._logger.info(f"[LIT] Getting all dispatches from lit-bridge")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {}}
        response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)
        self._logger.info(f"[LIT] Got all dispatches")
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
            self._logger.error(f"[LIT] Could not retrieve all dispatches, reason: {response['body']}")
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        self._logger.info(f"[LIT] All Dispatches - {len(response['body'])} - took {time.time() - start_time}")
        response_dispatch['vendor'] = 'LIT'
        response_dispatch['list_dispatch'] = [
            lit_mapper.map_get_dispatch(d) for d in response['body']['DispatchList']]

        return jsonify(response_dispatch), response["status"], None

    # Create Dispatch - POST - /lit/dispatch
    async def lit_create_dispatch(self):
        self._logger.info(f"[LIT] Creating new dispatch from lit-bridge")
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
        self._logger.info(f"[LIT] payload: {body}")
        dispatch_request = lit_mapper.map_create_dispatch(body)
        request_body = dict()
        request_body['RequestDispatch'] = dispatch_request

        payload = {"request_id": uuid(), "body": request_body}
        response = await self._event_bus.rpc_request("lit.dispatch.post", payload, timeout=30)
        self._logger.info(f"[LIT] Create dispatch response: {response}")

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
                f"[LIT] Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")
            ticket_id = body.get("mettel_bruin_ticket_id")
            slack_msg = f"[dispatch-portal-backend] [LIT] Dispatch Created [{dispatch_num}] with ticket id: " \
                        f"{ticket_id}"
            self._logger.info(slack_msg)
            await self._notifications_repository.send_slack_message(slack_msg)
            await self._process_note(dispatch_num, body)
        else:
            self._logger.info(f"[LIT] Dispatch not created - {payload} - took {time.time() - start_time}")
            error_response = {'code': response['status'], 'message': response['body']}
            return jsonify(error_response), response['status'], None
        return jsonify(response_dispatch), HTTPStatus.OK, None

    # Update Dispatch - PATCH - /lit/dispatch
    async def lit_update_dispatch(self):
        self._logger.info(f"[LIT] Updating dispatch from lit-bridge")
        start_time = time.time()
        body = await request.get_json()
        self._logger.info(f"[LIT] Updating dispatch from lit-bridge with body: {body}")
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

        self._logger.info(f"[LIT] Updating dispatch [{dispatch_number}] from lit-bridge")
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
            self._logger.info(f"[LIT] Dispatch not updated - {payload} - took {time.time() - start_time}")
            error_response = {'code': response['status'], 'message': response['body']}
            return jsonify(error_response), response['status'], None
        return jsonify(response_dispatch), HTTPStatus.OK, None

    # Upload File to Dispatch - POST - /lit/dispatch/<dispatch_number>/upload-file
    async def lit_upload_file_to_dispatch(self, dispatch_number):
        try:
            start_time = time.time()
            self._logger.info(f"[LIT] Uploading file to dispatch [{dispatch_number}] from lit-bridge")
            content_length = request.headers.get('content-length', None)
            self._logger.info(f"[LIT] File content length -- {content_length}")
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
                self._logger.info(f"[LIT] Uploaded Dispatch File [{dispatch_number}] "
                                  f"- {len(body)} bytes - took {time.time() - start_time}")
                response_dispatch['id'] = dispatch_number
                response_dispatch['vendor'] = 'lit'
                response_dispatch['file_id'] = response['body']['Message'].split(':')[1]
            else:
                self._logger.error(f"[LIT] Error Upload Dispatch File: {response['body']}")
                error_response = {'code': response['status'], 'message': response['body']}
                return jsonify(error_response), response['status'], None
            return jsonify(response_dispatch), HTTPStatus.OK, None
        except Exception as ex:
            self._logger.error(f"[LIT] Error: {ex}")
            error_response = {'code': ex.status_code, 'message': ex.description}
            return jsonify(error_response), ex.status_code

    # CTS endpoints
    # Get Dispatch - GET - /lit/dispatch/<dispatch_number>
    async def cts_get_dispatch(self, dispatch_number):
        self._logger.info(f"[CTS] Dispatch [{dispatch_number}] from cts-bridge")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {"dispatch_number": dispatch_number}}
        response = await self._event_bus.rpc_request("cts.dispatch.get", payload, timeout=30)
        self._logger.info(f"[CTS] Response get dispatch: {response}")
        response_dispatch = dict()
        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None
        if 'body' not in response or 'done' not in response['body'] or response['body']['done'] is False or \
                'records' not in response['body'] or response['body']['records'] is None or \
                len(response['body']['records']) == 0:
            self._logger.error(f"[CTS] Could not retrieve dispatch, reason: {response['body']}")
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        self._logger.info(f"[CTS] Dispatch [{dispatch_number}] - {response['body']} "
                          f"- took {time.time() - start_time}")
        dispatch = response['body']['records'][0]
        response_dispatch['id'] = dispatch.get('Name') if dispatch.get('Name') else dispatch_number
        response_dispatch['vendor'] = 'cts'
        response_dispatch['dispatch'] = cts_mapper.map_get_dispatch(dispatch)

        return jsonify(response_dispatch), response["status"], None

    # Get All Dispatches - GET - /cts/dispatch
    async def cts_get_all_dispatches(self):
        self._logger.info(f"[CTS] Getting all dispatches from cts-bridge")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {}}
        response = await self._event_bus.rpc_request("cts.dispatch.get", payload, timeout=30)
        self._logger.info(f"[CTS] Got all dispatches")
        response_dispatch = dict()
        if response['status'] == 500:
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        if 'body' not in response or 'done' not in response['body'] or response['body']['done'] is False or \
                'records' not in response['body'] or response['body']['records'] is None:
            self._logger.error(f"[CTS] Could not retrieve dispatch, reason: {response['body']}")
            error_response = {
                'code': response['status'], 'message': response['body']
            }
            return jsonify(error_response), response['status'], None

        all_dispatches = response['body'].get('records', [])
        self._logger.info(f"[CTS] All Dispatches - {len(all_dispatches)} - took {time.time() - start_time}")
        response_dispatch['vendor'] = 'cts'
        response_dispatch['list_dispatch'] = [cts_mapper.map_get_dispatch(d) for d in all_dispatches]

        return jsonify(response_dispatch), response["status"], None

    # Create Dispatch - POST - /cts/dispatch
    async def cts_create_dispatch(self):
        self._logger.info(f"[CTS] Creating new dispatch from cts-bridge")
        start_time = time.time()
        body = await request.get_json()

        try:
            validate(body, self._schema['components']['schemas']['new_dispatch_cts'])
        except jsonschema.exceptions.ValidationError as ve:
            self._logger.error(ve)
            error_message = "Schema not valid."
            self._logger.error(error_message)
            error_response = {'code': HTTPStatus.BAD_REQUEST, 'message': ve.message}
            return jsonify(error_response), HTTPStatus.BAD_REQUEST, None

        self._logger.info(f"payload: {body}")

        return_response = dict.fromkeys(["body", "status"])
        igz_dispatch_id = f"IGZ{uuid()}"
        ticket_id = body.get('mettel_bruin_ticket_id')

        # Check if already exists in bruin
        pre_existing_ticket_notes_response = await self._bruin_repository.get_ticket_details(ticket_id)
        pre_existing_ticket_notes_status = pre_existing_ticket_notes_response['status']
        pre_existing_ticket_notes_body = pre_existing_ticket_notes_response['body']

        if pre_existing_ticket_notes_status not in range(200, 300):
            err_msg = f"Error: could not retrieve ticket [{ticket_id}] details"
            self._logger.error(err_msg)
            return_response['status'] = 400
            return_response['body'] = err_msg
            # TODO: notify slack
            return jsonify(return_response), HTTPStatus.BAD_REQUEST, None

        ticket_notes = pre_existing_ticket_notes_body.get('ticketNotes', [])
        ticket_notes = [tn for tn in ticket_notes if tn.get('noteValue')]

        response_dispatch = dict()

        # Send email
        cts_body_mapped = cts_mapper.map_create_dispatch(body)
        email_template = render_email_template(cts_body_mapped)
        email_html = f'<div>{email_template}</div>'
        email_data = {
            'request_id': uuid(),
            'email_data': {
                'subject': f'CTS - Service Submission - {ticket_id}',
                'recipient': self._config.CTS_CONFIG["email"],
                'text': 'this is the accessible text for the email',
                'html': email_html,
                'images': [],
                'attachments': []
            }
        }
        response_send_email = await self._notifications_repository.send_email(email_data)
        response_send_email_status = response_send_email['status']
        if response_send_email_status not in range(200, 300):
            self._logger.error("[CTS] we could not send the email")
            error_response = {
                'code': response_send_email_status,
                'message': f'An error ocurred sending the email for ticket id: {ticket_id}'
            }
            return jsonify(error_response), response_send_email_status, None

        slack_msg = f"[dispatch-portal-backend] [CTS] Dispatch Requested by email [{igz_dispatch_id}]" \
                    f" with ticket id: {ticket_id}"
        self._logger.info(slack_msg)
        await self._notifications_repository.send_slack_message(slack_msg)

        # Append Note to bruin
        ticket_note = cts_get_dispatch_requested_note(body, igz_dispatch_id)
        await self._append_note_to_ticket(igz_dispatch_id, ticket_id, ticket_note)
        self._logger.info(f"Dispatch: {igz_dispatch_id} - {ticket_id} - Note appended: {ticket_note}")

        response_dispatch['id'] = igz_dispatch_id
        response_dispatch['vendor'] = 'CTS'
        self._logger.info(f"[CTS] Dispatch retrieved: {igz_dispatch_id} - took {time.time() - start_time}")

        return jsonify(response_dispatch), HTTPStatus.OK, None

    async def _append_note_to_ticket(self, dispatch_number, ticket_id, ticket_note):
        # Split the note if needed
        ticket_notes = textwrap.wrap(ticket_note, self.MAX_TICKET_NOTE, replace_whitespace=False)
        for i, note in enumerate(ticket_notes):
            self._logger.info(f"Appending note_{i} to ticket {ticket_id}")
            append_note_response = await self._bruin_repository.append_note_to_ticket(ticket_id, note)
            append_note_response_status = append_note_response['status']
            append_note_response_body = append_note_response['body']
            if append_note_response_status not in range(200, 300):
                self._logger.error(f"[process_note] Error appending note: `{note}` "
                                   f"Dispatch: {dispatch_number} "
                                   f"Ticket_id: {ticket_id} - Not appended")
                continue
            self._logger.info(f"[process_note] Note: `{note}` Dispatch: {dispatch_number} "
                              f"Ticket_id: {ticket_id} - Appended")
            self._logger.info(f"[process_note] Note appended. Response {append_note_response_body}")

    async def _process_note(self, dispatch_number, body):
        try:
            ticket_id = body['mettel_bruin_ticket_id']
            ticket_note = lit_get_dispatch_requested_note(body, dispatch_number)

            await self._append_note_to_ticket(dispatch_number, ticket_id, ticket_note)
        except Exception as ex:
            self._logger.error(f"[process_note] Error: {ex}")

    def _add_dispatch_to_cache(self, ticket_id, igz_dispatch_id):
        dispatch_from_cache = self._redis_client.hmget(self.PENDING_DISPATCHES_KEY, ticket_id)
        dispatch_from_cache = [d for d in dispatch_from_cache if d]
        if len(dispatch_from_cache) == 0:
            pending_dispatch = {
                ticket_id: igz_dispatch_id
            }
            self._logger.info(f"Adding {pending_dispatch} to cache")
            return self._redis_client.hmset(self.PENDING_DISPATCHES_KEY, pending_dispatch)
        else:
            self._logger.info(f"Error: {ticket_id} - {igz_dispatch_id} already exists in cache.")
            return False
