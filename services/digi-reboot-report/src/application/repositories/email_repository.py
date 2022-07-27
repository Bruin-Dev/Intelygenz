import base64
from datetime import datetime, timedelta

from shortuuid import uuid


class EmailRepository:
    def __init__(self, event_bus, config):
        self._event_bus = event_bus
        self._config = config

    async def send_email(self, digi_reboot_report, **kwargs):
        csv = "{}".format(kwargs.get("csv", "digi_reboot_report.csv"))

        yesterday_date = datetime.now() - timedelta(days=2)

        html = f"""\
        <html>
          <head></head>
          <body>
            <p>Please see more recent report with data through the end of {yesterday_date.strftime("%Y-%m-%d")}.
               <br>
               This report is generated by the MetTel IPA system.
            </p>
          </body>
        </html>
        """
        email_object = {
            "request_id": uuid(),
            "email_data": {
                "subject": f'DiGi Recovery Report ({(datetime.now()- timedelta(days=1)).strftime("%Y-%m-%d")}) ',
                "recipient": self._config.DIGI_CONFIG["recipient"],
                "text": "this is the accessible text for the email",
                "html": html,
                "images": [],
                "attachments": [
                    {"name": csv, "data": base64.b64encode(digi_reboot_report.encode("utf-8")).decode("utf-8")}
                ],
            },
        }
        await self._event_bus.rpc_request("notification.email.request", email_object, timeout=60)
