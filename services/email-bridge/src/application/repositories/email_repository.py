from http import HTTPStatus


class EmailRepository:
    def __init__(self, email_client):
        self._email_client = email_client

    def send_to_email(self, msg):
        status = self._email_client.send_to_email(msg)
        if status == HTTPStatus.OK:
            body = f"Successfully sent email with message {msg}"
        else:
            body = f"Failed to send email with message {msg}"

        return {"body": body, "status": status}
