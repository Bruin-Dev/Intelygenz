import time
from http import HTTPStatus

import asyncio
from datetime import datetime

from quart import jsonify, request, current_app
from quart_openapi import Resource, PintBlueprint
from shortuuid import uuid

from config import config

lit_bp = PintBlueprint('lit', __name__, url_prefix='/lit',
                       base_model_schema=config.DISPATCH_PORTAL_CONFIG['schema_path'])

# TODO: retrieve all schemas
expected_create_dispatch = lit_bp.create_ref_validator('new_dispatch_lit', 'schemas')


@lit_bp.route('/dispatch', methods=['POST', 'PATCH'], strict_slashes=False)
@lit_bp.route('/dispatch/<dispatch_number>', methods=['GET'], strict_slashes=False)
class LitDispatch(Resource):
    async def get(self, dispatch_number):
        current_app._logger.info(f"Retrieving dispatch <{dispatch_number}> from lit-brige")
        start_time = time.time()
        payload = {"request_id": uuid(), "body": {"dispatch_number": dispatch_number}}
        response = await current_app._event_bus.rpc_request("lit.dispatch.get",
                                                            payload, timeout=30)
        current_app._logger.info(f"Dispatch retrieved: {dispatch_number} - "
                                 f"{response['body']} - took {time.time() - start_time}")
        return jsonify(response['body']), response["status"], None

    @lit_bp.expect((expected_create_dispatch, 'application/json', {}))
    async def post(self):
        current_app._logger.info(f"Creating new dispatch from lit-brige")
        start_time = time.time()
        body = await request.get_json()
        current_app._logger.info(f"payload: {body}")

        body = {k.lower(): v for k, v in body.items()}

        # TODO: map body request with lit RequestDispatch
        dispatch_request = {
            "date_of_dispatch": body['date_of_dispatch'],
            "site_survey_quote_required": body['site_survey_quote_required'],
            "local_time_of_dispatch": body['time_of_dispatch'],
            "time_zone_local": body['time_zone'],
            "job_site": body["job_site"],
            "job_site_street": body["job_site_street"],
            "job_site_city": body["job_site_city"],
            "job_site_state": body["job_site_state"],
            "job_site_zip_code": body["123321"],
            "job_site_contact_name_and_phone_number": f'{body["job_site_contact_name"]} '
                                                      f'{body["job_site_contact_number"]}',
            "special_materials_needed_for_dispatch": body["materials_needed_for_dispatch"],
            "scope_of_work": body["scope_of_work"],
            "mettel_tech_call_in_instructions": body["mettel_tech_call_in_instructions"],
            "name_of_mettel_requester": body["name_of_mettel_requester"],
            "mettel_department": body["mettel_department"],
            "mettel_requester_email": body["mettel_requester_email"],
            # The Lit API doesn`t accept this parameter
            # "mettel_bruin_ticketid": str(body["mettel_bruin_ticket_id"]),
        }

        request_body = dict()
        request_body['RequestDispatch'] = dispatch_request

        payload = {"request_id": uuid(), "body": request_body}
        response = await current_app._event_bus.rpc_request("lit.dispatch.post", payload, timeout=30)
        current_app._logger.info(response)
        if 'body' in response and 'Dispatch' in response['body'] \
                and 'Dispatch_Number' in response['body']['Dispatch']:
            dispatch_num = response['body']['Dispatch']['Dispatch_Number']
            current_app._logger.info(
                f"Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")
        else:
            current_app._logger.info(f"Dispatch not created - {payload} - took {time.time() - start_time}")
        return jsonify(response['body']), response["status"], None

    async def patch(self):
        start_time = time.time()
        body = await request.get_json()
        if 'Dispatch_Number' not in body:
            current_app._logger.error("`Dispatch_Number` field not provided")
            return jsonify({}), HTTPStatus.BAD_REQUEST, None

        dispatch_number = body['Dispatch_Number']

        request_body = dict()
        request_body['RequestDispatch'] = body

        current_app._logger.info(f"Updating dispatch <{dispatch_number}> from lit-brige")
        current_app._logger.info(f"payload: {body}")

        payload = {"request_id": uuid(), "body": request_body}
        response = await current_app._event_bus.rpc_request("lit.dispatch.update", payload, timeout=30)
        current_app._logger.info(response)
        if 'body' in response and 'Dispatch' in response['body'] \
                and response['body']['Dispatch'] \
                and 'Dispatch_Number' in response['body']['Dispatch']:
            dispatch_num = response['body']['Dispatch']['Dispatch_Number']
            current_app._logger.info(
                f"Dispatch retrieved: {dispatch_num} - took {time.time() - start_time}")
        else:
            current_app._logger.info(f"Dispatch not updated - {payload} - took {time.time() - start_time}")
        return jsonify(response['body']), response["status"], None


@lit_bp.route('/dispatch/<dispatch_number>/upload-file', methods=['POST'], strict_slashes=False)
class LitDispatchUpload(Resource):
    async def post(self, dispatch_number):
        start_time = time.time()

        # file_key = current_app._redis_client.hget("dispatch_files", dispatch_number)
        # if file_key is None:
        #     current_app._logger.error("file_key no provided.")
        #     return jsonify(), HTTPStatus.OK, None
        # current_app._redis_client.hset("dispatch_files", dispatch_number, number)

        file_key = current_app._redis_client.hget("dispatch_files", dispatch_number)
        if file_key is None:
            current_app._logger.error("file_key no provided.")
            return jsonify(), HTTPStatus.BAD_REQUEST, None
        current_app._redis_client.hset("dispatch_files", dispatch_number, 0)
        # payload_body = await request.get_data(raw=True)
        await asyncio.sleep(0.1)


'''
class LitTest2(Resource):
    @lit_bp.route('/dispatch/<dispatch_number>/upload-file', methods=['POST'])
    async def upload_file(self, dispatch_number):
        file_content_in_base64 = """
                LARGE FILE IN BASE64
                """
        payload = await request.get_data(raw=True)
        # send file key to retrieve it in the lit-bridge
        file_key = f"{dispatch_number}_{str(int(datetime.utcnow().timestamp()))}"

        # self._redis_client.hset("dispatch_files", file_key, file_content_in_base64)
        # payload = self._redis_client.hget("dispatch_files", file_key)
        # self._redis_client.hdel("dispatch_files", file_key, 1)
'''
