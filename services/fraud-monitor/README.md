# Fraud monitor
* [Description](#description)
* [Workflow](#workflow)  
* [Capabilities used](#capabilities-used) 
* [Running in docker-compose](#running-in-docker-compose)

# Description
The goal of the `fraud-monitor` service is to get unread fraud warning emails and create fraud tickets for them.

# Workflow
Every 5 minutes the `fraud-monitor` makes an RPC request to get recent unread emails from the configured `inbox_email` that were sent by anyone in the configured `sender_emails_list`. 
Then we loop through each email, skipping the ones that are invalid or not a fraud warning.

In order to create a fraud ticket we need a `DID`, which we can extract from the email body.
Then we need to make an RPC request with that `DID` to the Bruin bridge to get a service number and a client ID.

Once the ticket has been created, or if we find an existing ticket for the current email, we append the main content of the email body as a note to this ticket.

If the email was processed successfully we make an RPC request to mark it as read,
otherwise we need to keep it unread in order to reattempt processing it next time the `fraud-monitor` runs.

# Capabilities used
- [Notifier](../notifier/README.md)
- [Bruin Bridge](../bruin-bridge/README.md)

![IMAGE: fraud-monitor_microservice_relationships](/docs/img/system_overview/use_cases/fraud-monitor_microservice_relationships.png)

# Running in docker-compose
`docker-compose up --build nats-server notifier bruin-bridge fraud-monitor`
