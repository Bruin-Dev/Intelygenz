**Table of contents**

- [Email Bridge](#email-bridge)
  - [Description](#email-bridge-description)
- [Send to Email](#send-to-email)
  - [Description](#send-to-email_description)
  - [Request message](#send-to-email_request_message)
  - [Response message](#send-to-email_response_message)
- [Get Unread Emails](#get-unread-emails)
  - [Description](#get-unread-emails_description)
  - [Request message](#get-unread-emails_request_message)
  - [Response message](#get-unread-emails_response_message)
- [Mark Email as Read](#mark-email-as-read)
  - [Description](#mark-email-as-read_description)
  - [Request message](#mark-email-as-read_request_message)
  - [Response message](#mark-email-as-read_response_message)  
- [Running in docker-compose](#running-in-docker-compose)

# Email Bridge

## Description <a name="email-bridge-description"></a>

The email bridge receives requests messages, and based on the topic that it received the message from, it can send an email

## Send to Email

### Description <a name="send-to-email_description"></a>

The email bridge receives a request message from topic `notification_email_request`, and then makes a callback to the 
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

## Get Unread Emails

### Description <a name="get-unread-emails_description"></a>
The email bridge receives a request message from topic `get.email.request`, and then makes a callback to the 
`get_unread_emails` function. It then extracts the `email_account` and `email_filter` from the body of the request message if it exists and is not empty.
Then it sends both of those values to the email reader repository. 

The repository will first search if the `email_account` exist in the config's `MONITORABLE_EMAIL_ACCOUNTS` dictionary. It will then
return the associated password if found then send both the `email_account`, the associated password, and the `email_filter` to the client.

The client should be returning all the unread email from the all emails folder of the `email_account`, sorted by sent date, given they were sent
by email addresses specified in the `email_filter` and they were sent the day the rpc request was made.


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
The email bridge receives a request message from topic `mark.email.read.request`, and then makes a callback to the 
`mark_email_as_read` function. It then extracts the `email_account` and `msg_uid` from the body of the request message if it exists and is not empty.
Then it sends both of those values to the email reader repository. 

The repository will first search if the `email_account` exist in the config's `MONITORABLE_EMAIL_ACCOUNTS` dictionary. It will then
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

`docker-compose up --build redis nats-server email-bridge`
