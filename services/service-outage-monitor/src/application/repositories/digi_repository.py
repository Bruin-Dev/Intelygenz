import json
import logging

from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class DiGiRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def reboot_link(self, serial_number, ticket_id, logical_id):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {"velo_serial": serial_number, "ticket": str(ticket_id), "MAC": logical_id},
        }

        try:
            logger.info(f"Rebooting DiGi link of ticket {ticket_id} from Bruin...")
            response = await self._nats_client.request("digi.reboot", to_json_bytes(request), timeout=90)
            response = json.loads(response.data)
            logger.info(f"Got details of ticket {ticket_id} from Bruin!")
        except Exception as e:
            err_msg = f"An error occurred when attempting a DiGi reboot for ticket {ticket_id} -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while attempting a DiGi reboot for ticket {ticket_id} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    def is_digi_link(self, link):
        for header in self._config.DIGI_HEADERS:
            if header in link["logical_id"]:
                return True
        return False

    def get_digi_links(self, logical_id_list):
        return [link for link in logical_id_list if self.is_digi_link(link)]

    @staticmethod
    def get_interface_name_from_digi_note(digi_note):
        if digi_note and digi_note.get("noteValue"):
            interface_name = None
            lines = digi_note.get("noteValue").splitlines()
            for line in lines:
                if line and len(line) > 0 and "Interface: " in line:
                    interface_name = "".join(ch for ch in line)
                    break
            if interface_name is None or interface_name.strip() == "":
                return ""
            return interface_name.strip().replace("Interface: ", "")

        return ""
