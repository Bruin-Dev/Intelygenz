# Table of contents
- [Notifier](#notifier)
  * [Desciption](#description)
- [Send to Email](#send-to-email)
  * [Description](#description-1)
  * [Request message](#request-message)
  * [Response message](#response-message)
- [Send to Slack](#send-to-slack)
  * [Description](#description-2)
  * [Request message](#request-message-1)
  * [Response message](#response-message-1)
- [Running in docker-compose](#running-in-docker-compose)

# Notifier 
###Description
The notifier receives requests messages, and based on the topic that it received the message from, it can either send an email
or send a message to our slack channel.

## Send to Email
### Description
The notifier receives a request message from topic `notification_email_request`, and then makes a callback to the 
`send_to_email` function. It then extracts the `email_data` dictionary from the request message if it exists and is not empty.
Then it sends the email data to the email repository which sends it to the email client.

The email client will attempt to send the email in a try/catch. The email client will first need to login using 
the library `smtplib` and the fields `sender_email` and `password` from the configs file. From there it will use
`MIMEMultipart` to format the data from the `email_data` dictionary into a format that can be sent as an email. Then
it uses the `sender_email` from configs, the `recipient` field from the `email_data` dictionary, and the newly formatted
`MIMEMultipart` message to send the email. If it's sent successfully then a status code of 200 will be returned. And
the send_to_email function will put this in a dictionary and publish it to the topic identified that was built by NATS under
the hood. If any error occurs during the process then an error message is printed out and a status code of
500 is returned and published instead. 

### Request message
 ```
{
    'request_id': 123,
    'email_data': {
        'subject': 'Some Subject',
        'recipient': self._config.TRIAGE_CONFIG["recipient"],
        'text': 'this is the accessible text for the email',
        'html': email_html,
        'images': [],
        'attachments': []
    }
}
```
### Response message
```
{
   'request_id': msg_dict['request_id'], 
   'status': 200
}
```
##Send to Slack
### Description
The notifier receives a request message from topic `notification_slack_request`, and then makes a callback to the 
`send_to_slack` function. Which extracts the `message` field from the request message and sends it to slack_repository. 

In the slack repository, a dictionary is created with the key `text` and the value is the `message` field passed by 
`send_to_slack` converted into string format. This new dictionary is then passed down to the slack client. 

The slack client receives the message passed down from the slack repository. And prepares to make a `POST` call to 
to a webhook url, which is provided in the config file located in the config folder of this 
microservice. Any `POST` calls made to that url will post to a slack channel. It however
first must check that the webhook url is a valid url by checking to see if the string 
`https://` is within the url.  Once that is cleared, it then makes the request call. A message will be 
printed to the console and returned to determine if the message was successfully sent or not based on the status
code of the request call. 200 is a success and anything else is a failure.

This returned message goes back to the `send_to_slack` function to publish it to the topic that was built by NATS under
the hood.
### Request message
```
{
    'request_id': 123,
    'message':'Some message',
}
```
### Response message
```
{
   'request_id': msg_dict['request_id'], 
   'status': 200
}
```
# Running in docker-compose 
`docker-compose up --build nats-server notifier `