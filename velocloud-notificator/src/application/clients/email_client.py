import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.nonmultipart import MIMENonMultipart
from email.charset import Charset, BASE64
import base64


class EmailClient:

    def __init__(self, config, logger):
        self._config = config
        self._logger = logger
        self.email_login()

    def email_login(self):
        try:
            self._email_server = smtplib.SMTP('smtp.gmail.com:587')
            self._email_server.ehlo()
            self._email_server.starttls()
            self._email_server.login(self._config.EMAIL_CONFIG['sender_email'], self._config.EMAIL_CONFIG['password'])
        except Exception:
            self._logger.exception('Error: Could not login')

    def send_to_email(self, msg):
        try:
            mime_msg = MIMEMultipart('related')
            mime_msg['From'] = self._config.EMAIL_CONFIG['sender_email']
            mime_msg['To'] = msg["recipient"]
            mime_msg['Subject'] = msg["subject"]

            mime_msg_alternative = MIMEMultipart('alternative')
            mime_msg_alternative.attach(MIMEText(msg["text"], 'text'))
            mime_msg_alternative.attach(MIMEText(msg["html"], 'html'))
            mime_msg.attach(mime_msg_alternative)

            for image in msg['images']:
                name = image['name']
                data = base64.b64decode(image['data'].encode('utf-8'))
                mime_img = MIMEImage(data)
                mime_img.add_header('Content-ID', f'<{name}>')
                mime_msg.attach(mime_img)

            for att in msg['attachments']:
                attachment = (MIMENonMultipart('text', 'csv', charset='utf-8'))
                attachment_name = att["name"]

                attachment.add_header('Content-Disposition', 'attachment', filename=attachment_name)
                cs = Charset('utf-8')
                cs.body_encoding = BASE64
                attachment.set_payload(base64.b64decode(att["data"].encode('utf-8')), charset=cs)
                mime_msg.attach(attachment)

            self._email_server.sendmail(self._config.EMAIL_CONFIG['sender_email'],
                                        msg["recipient"],
                                        mime_msg.as_string())

            self._logger.info("Success: Email sent!")
            return 200

        except Exception:
            self._logger.exception('Error: Email not sent')
            return 500
