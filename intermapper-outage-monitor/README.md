# Table of contents
  * [Description](#description)
  * [Overview](#overview)  
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `intermapper-outage-monitor` is to grab unread emails and create any outage tickets based on the email
contents.

# Overview
Every 10 mins the `intermapper-outage-monitor` makes a rpc request to grab all the unread emails in the inbox of the `inbox_email` config, and
look for emails from senders in the `sender_emails_list` config. 

We then loop through each email. If the `msg_uid` is not `None` or `-1` we make another rpc request to mark that email as read.
Then we parse the `body` of the email to break it down into a dictionary. Breaking it down into a dictionary makes it alot easier to 
check if the `event` of the InterMapper email is any of the events in the `intermapper_events` list (`['Down', 'Critical', 'Alarm', 'Warning']`).
After that we then grab the `asset_id` by parsing through the string in the `name` section of the dictionary.

In order to create a ticket from the InterMapper email we need a `circuit_id` which acts as our service number and the `client_id`.
And to get our `circuit_id` and `client_id` we make a rpc call to the bruin bridge, with the `asset_id` included in the request message, 
to return a dict with the `circuit_id` and `client_id`.

Once the ticket has been created, we then can proceed to send a slack message alerting the notifcations channel we have created a ticket.
Which is then followed up by appending the full `body` of the InterMapper email as the triage note to this new ticket.

# Capabilities used
- [Bruin Bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build nats-server notifier bruin_bridge intermapper-outage-monitor`



