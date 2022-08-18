import base64
import logging
import smtplib
from dataclasses import dataclass
from email.charset import BASE64, Charset
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class EmailClient:
    config: Dict
    email_server: smtplib.SMTP = None
    EMAIL_SEPARATOR = ", "

    def email_login(self):
        self._email_server = smtplib.SMTP("smtp.gmail.com:587")
        self._email_server.ehlo()
        self._email_server.starttls()
        self._email_server.login(
            self.config.EMAIL_DELIVERY_CONFIG["email"],
            self.config.EMAIL_DELIVERY_CONFIG["password"],
        )

    def send_to_email(self, msg):
        try:
            self.email_login()
            mime_msg = MIMEMultipart("related")
            mime_msg["From"] = self.config.EMAIL_DELIVERY_CONFIG["email"]
            mime_msg["To"] = msg["recipient"]
            mime_msg["Subject"] = msg["subject"]

            mime_msg_alternative = MIMEMultipart("alternative")
            mime_msg_alternative.attach(MIMEText(msg["text"], "text"))
            mime_msg_alternative.attach(MIMEText(msg["html"], "html"))
            mime_msg.attach(mime_msg_alternative)

            for image in msg["images"]:
                name = image["name"]
                data = base64.b64decode(image["data"].encode("utf-8"))
                mime_img = MIMEImage(data)
                mime_img.add_header("Content-ID", f"<{name}>")
                mime_msg.attach(mime_img)

            for att in msg["attachments"]:
                attachment = MIMENonMultipart("text", "csv", charset="utf-8")
                attachment_name = att["name"]

                attachment.add_header("Content-Disposition", "attachment", filename=attachment_name)
                cs = Charset("utf-8")
                cs.body_encoding = BASE64
                attachment.set_payload(base64.b64decode(att["data"].encode("utf-8")), charset=cs)
                mime_msg.attach(attachment)

            self._email_server.sendmail(
                self.config.EMAIL_DELIVERY_CONFIG["email"],
                msg["recipient"].split(self.EMAIL_SEPARATOR),
                mime_msg.as_string(),
            )

            logger.info("Success: Email sent!")
            self._email_server.quit()
            return 200

        except Exception:
            logger.exception("Error: Email not sent")
            return 500
