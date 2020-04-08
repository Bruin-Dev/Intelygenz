class UploadFile:

    def __init__(self, logger, config, event_bus, lit_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._lit_repository = lit_repository

    async def upload_file(self, msg):
        upload_file_response = {"request_id": msg["request_id"], "body": None,
                                "status": None}

        if msg.get("body") is None:
            upload_file_response["status"] = 400
            upload_file_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], upload_file_response)
            return
        upload_file_required_keys = ["dispatch_number", "payload", "file_name"]
        if all(key in msg["body"].keys() for key in upload_file_required_keys):
            payload = msg["body"]["payload"]
            dispatch_number = msg["body"]["dispatch_number"]
            file_name = msg["body"]["file_name"]
            file_content_type = "application/octet-stream"

            if 'file_content_type' in msg["body"].keys():
                file_content_type = msg["body"]["file_content_type"]
            self._logger.info(f"Upload_file_request for dispatch: {dispatch_number}")
            upload_file = self._lit_repository.upload_file(dispatch_number, payload, file_name, file_content_type)
            upload_file_response["body"] = upload_file["body"]
            upload_file_response["status"] = upload_file["status"]
        else:
            upload_file_response["body"] = f'Must include the following keys in request: {upload_file_required_keys}'
            upload_file_response["status"] = 400

        await self._event_bus.publish_message(msg['response_topic'], upload_file_response)
