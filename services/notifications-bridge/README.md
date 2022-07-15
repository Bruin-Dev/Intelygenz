**Table of contents**

- [Notifications Bridge](#notifications-bridge)
  - [Description](#notifications-bridge-description)
- [Send to Slack](#send-to-slack)
  - [Description](#send-to-slack_description)
  - [Request message](#send-to-slack_request_message)
  - [Response message](#send-to-slack_response_message)
- [Running in docker-compose](#running-in-docker-compose)

# Notifications Bridge

## Description <a name="notifications-bridge-description"></a>

The notifications-bridge receives requests messages, and based on the topic that it received the message from, it can send a message to our slack channel.

## Send to Slack

### Description <a name="send-to-slack_description"></a>

There are two slack channels used for sending notifications:

- *mettel-notifications-dev*: Used for sending notifications to slack from development environments.

- *mettel-notifications*: Used for sending notifications to slack from the production environment, that is, from the `master` branch

The notifications-bridge receives a request message from topic `notification_slack_request`, and then makes a callback to the 
`send_to_slack` function. Which extracts the `message` field from the request message and sends it to slack_repository. 

In the slack repository, a dictionary is created with the key `text` and the value is the `message` field passed by 
`send_to_slack` converted into string format. This new dictionary is then passed down to the slack client. 

The slack client receives the message passed down from the slack repository. And prepares to make a `POST` call
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

# Running in docker-compose

`docker-compose up --build redis nats-server notifications-bridge`
