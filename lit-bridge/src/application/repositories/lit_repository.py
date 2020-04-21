import json
from quart import jsonify, request
from http import HTTPStatus


class LitRepository:

    def __init__(self, lit_client, logger, config):
        self._lit_client = lit_client
        self._logger = logger
        self._config = config

    async def create_dispatch(self):
        payload = await request.get_json()
        response = self._lit_client.create_dispatch(payload)
        self._logger.info(f"create_dispatch_response: {response}")
        return jsonify(response), response["status"]

    def get_dispatch(self, dispatch_number):
        response = self._lit_client.get_dispatch(dispatch_number)
        self._logger.info(f"get_dispatch_response: {response}")
        return jsonify(response), response["status"]

    async def update_dispatch(self, dispatch_number):
        payload = await request.get_json()
        if payload and 'RequestDispatch' in payload.keys() and 'Dispatch_Number' not in payload['RequestDispatch']:
            payload['RequestDispatch']['Dispatch_Number'] = dispatch_number
        response = self._lit_client.update_dispatch(payload)
        self._logger.info(f"update_dispatch_response: {response}")
        return jsonify(response), response["status"]

    async def upload_file(self, dispatch_number):
        payload = await request.get_data(raw=True)
        file_content_type = "application/octet-stream"
        if 'Content-Type' in request.headers.keys():
            file_content_type = request.headers["Content-Type"]
        if 'filename' not in request.headers.keys():
            return jsonify({"body": "filename not found in headers.",
                            "status": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST
        file_name = request.headers['filename']
        response = self._lit_client.upload_file(dispatch_number, payload, file_name, file_content_type)
        return jsonify(response), response["status"]
