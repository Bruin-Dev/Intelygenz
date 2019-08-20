# Table of contents
  * [Description](#description)
  * [Work Flow](#work-flow)
  * [Behaviour in dev and in pro](#behaviour-in-development-and-in-production)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The service outage triage's job is to search through the bruin tickets and append our triage as a note to any
tickets that match the filter we have set.

# Work Flow
Every minute the apscheduler calls the service outage triage's `_poll_tickets` function. In that function the service
makes an rpc request to the bruin bridge to receive all the tickets that match the client_id, ticket_status, and category
that we provide to the bridge.

Once all tickets are received we run that through another filter with the function `_filtered_ticket_details`.
Which makes another rpc request to the bruin bridge to receive the ticket details for each ticket. With
the details we can see if the ticket matches the serial number of the edge we're currently looking to append 
tickets to. Then once we find a ticket that matches that we check if the triage has already been appended.

`_Filtered_ticket_details` function should return a list of ticket ids that needs the triage appended.
So now we create an ordered dict using the function ` _compose_ticket_note_object` with parameters of the edge status
and edge events of the edge we're currently monitoring ,
`{"host": "mettel.velocloud.net", "enterprise_id": 137, "edge_id": 1602}`, obtained through rpc calls.

That ordered dict is now our triage. And then based on our current environment, development or production, 
we send an email of the triage or append the triage as a note. It is then followed by a slack message confirming triage
has been appended or sent with a url to the ticket and the environment in which the action took place.


# Behaviour in development and in production
In our development environment we are taking the ordered dict created for the triage and converting it into an email 
object that we can send to the notifier to create and send out an email.

In our production environment we are taking the ordered dict created for the triage and convert it into one long 
string. That string will be appended as a note using the bruin bridge for the ticket with the current ticketid
 we're dealing with .

The check for whether you're in development or production is needed so when we're making changes to the service outage
triage and we're testing it we are not appending anything to real tickets. We only append the triage when we deploy in
production. 

# Capabilities used
- [Bruin bridge](../bruin-bridge/README.md)
- [Velocloud bridge](../velocloud-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose 
`docker-compose up --build service-outage-triage bruin-bridge velocloud-bridge notifier nats-streaming `
