**Table of contents**

- [Notifier](#notifier)
  - [Description](#notifier-description)
- [Send to Email](#send-to-email)
  - [Description](#send-to-email_description)
  - [Request message](#send-to-email_request_message)
  - [Response message](#send-to-email_response_message)
- [Send to Slack](#send-to-slack)
  - [Description](#send-to-slack_description)
  - [Request message](#send-to-slack_request_message)
  - [Response message](#send-to-slack_response_message)
- [Get Unread Emails](#get-unread-emails)
  - [Description](#get-unread-emails_description)
  - [Request message](#get-unread-emails_request_message)
  - [Response message](#get-unread-emails_response_message)
- [Mark Email as Read](#mark-email-as-read)
  - [Description](#mark-email-as-read_description)
  - [Request message](#mark-email-as-read_request_message)
  - [Response message](#mark-email-as-read_response_message)  
- [Running in docker-compose](#running-in-docker-compose)

# Notifier

## Description <a name="notifier-description"></a>

The notifier receives requests messages, and based on the topic that it received the message from, it can either send an email
or send a message to our slack channel.

## Send to Email

### Description <a name="send-to-email_description"></a>

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

### Request message <a name="send-to-email_request_message"></a>

 ```json
{
    'request_id': 123,
    'email_data': {
        'subject': 'Some Subject',
        'recipient': 'some-email',
        'text': 'this is the accessible text for the email',
        'html': email_html,
        'images': [],
        'attachments': []
    }
}
```

### Response message <a name="send-to-email_response_message"></a>

```json
{
   'request_id': msg_dict['request_id'], 
   'status': 200
}
```

## Send to Slack

### Description <a name="send-to-slack_description"></a>

There are two slack channels used for sending notifications:

- *mettel-notifications-dev*: Used for sending notifications to slack from development environments.

- *mettel-notifications*: Used for sending notifications to slack from the production environment, that is, from the `master` branch

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

### Request message <a name="send-to-slack_request_message"></a>

```json
{
    'request_id': 123,
    'message':'Some message',
}
```

### Response message <a name="send-to-slack_response_message"></a>

```json
{
   'request_id': msg_dict['request_id'], 
   'status': 200
}
```

## Get Unread Emails

### Description <a name="get-unread-emails_description"></a>
The notifier receives a request message from topic `get.email.request`, and then makes a callback to the 
`get_unread_emails` function. It then extracts the `email_account` and `email_filter` from the body of the request message if it exists and is not empty.
Then it sends both of those values to the email reader repository. 

The repository will first search if the `email_account` exist in the config's `EMAIL_ACCOUNTS` dictionary. It will then 
return the associated password if found then send both the `email_account`, the associated password, and the `email_filter` to the client.

The client should be returning all the unread email, from the all emails folder of the `email_account` given that were sent
by email addresses specified in the `email_filter` and that were sent that the day the rpc request was made.


### Request message <a name="get-unread-emails_request_message"></a>

 ```json
{
    'request_id': 123,
    'body': {
              'email_account': 'fakeemail@gmail.com',
              'email_filter': ['senderemail@gmail.com']
    }
}
```

### Response message <a name="gget-unread-emails_response_message"></a>

```json
{
   'request_id': msg_dict['request_id'], 
   'body': [{'message': msg, 'subject': subject, 'body': body, 'msg_uid': msg_uid}] #List of unread emails
   'status': 200
}
```

## Mark Email as Read

### Description <a name="mark-email-as-read_description"></a>
The notifier receives a request message from topic `mark.email.read.request`, and then makes a callback to the 
`mark_email_as_read` function. It then extracts the `email_account` and `msg_uid` from the body of the request message if it exists and is not empty.
Then it sends both of those values to the email reader repository. 

The repository will first search if the `email_account` exist in the config's `EMAIL_ACCOUNTS` dictionary. It will then 
return the associated password if found then send both the `email_account`, the associated password, and the `msg_uid` to the client.

The client should be marking the email with the given `msg_uid` as read. If it is successful it should return a True back
to the action level.

### Request message <a name="mark-email-as-read_request_message"></a>

 ```json
{
    'request_id': 123,
    'body': {
               'email_account': 'fakeemail@gmail.com',
               'msg_uid': '123'
    }
}
```

### Response message <a name="mark-email-as-read_response_message"></a>
```json
{
   'request_id': msg_dict['request_id'], 
   'body': 'Successfully marked message {msg_uid} as read',
   'status': 200
}
```

# Running in docker-compose

`docker-compose up --build redis nats-server notifier`