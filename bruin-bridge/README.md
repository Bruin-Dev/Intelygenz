# Table of contents
  * [Bruin API](#bruin-api)
    * [Description](#description)
    * [Links](#links)
  * [Get All Tickets](#get-all-tickets)
    * [Description](#description-1)
    * [Request message](#request-message)
    * [Response message](#response-message)
  * [Get Tickets Details](#get-tickets-details)
    * [Description](#description-2)
    * [Request message](#request-message-1)
    * [Response message](#response-message-1)
  * [Get Tickets Details by edge serial](#get-tickets-details-by-edge-serial)
    * [Description](#description-3)
    * [Request message](#request-message-2)
    * [Response message](#response-message-2)
  * [Post notes to Ticket](#post-notes-to-ticket)
    * [Description](#description-4)
    * [Request message](#request-message-3)
    * [Response message](#response-message-3)
  * [Post Ticket](#post-ticket)
    * [Description](#description-5)
    * [Request message](#request-message-4)
    * [Response message](#response-message-4)
  * [Open Ticket](#open-ticket)
    * [Description](#description-6)
    * [Request message](#request-message-5)
    * [Response message](#response-message-5)
  * [Resolve Ticket](#resolve-ticket)
    * [Description](#description-7)
    * [Request message](#request-message-6)
    * [Response message](#response-message-6)
  * [Get Management status](#get-management-status)
    * [Description](#description-8)
    * [Request message](#request-message-7)
    * [Response message](#response-message-7)      
    * [Response message](#response-message-6)      
  * [Post Outage Ticket](#post-outage-ticket)
    * [Description](#description-9)
    * [Request message](#request-message-8)
    * [Response message](#response-message-8)
- [Running in docker-compose](#running-in-docker-compose)


# Bruin API
### Description

Bruin Bridge is used to make calls to the Bruin API. The main calls include [getting all tickets](#get-all-tickets), [getting ticket details](#get-tickets-details),
[appending notes to tickets](#post-notes-to-ticket), and creating tickets.

### Links
Bruin swagger:
https://api.bruin.com/index.html

Bruin app:
https://app.bruin.com

# Get All Tickets
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.request` it makes a callback
to function `get_all_tickets`.  The request message, contains all of the fields needed to filter the tickets and
receive only relevant tickets. These fields include `ticket_id`, `client_id`,  `ticket_status`, and `category`. 
Once all of the fields are extracted from the request message, a call to the bruin repository is made.

In the bruin repository, it loops through the `ticket_status` field which should be a list. Each time it will make
a call to the bruin client to receive all the tickets matching the filter. At the end of the loop, all the tickets returned
from the bruin clients for each status should be combined into one big list of tickets. Which gets sent back to the callback
function. If any of the tickets received from bruin client return `None` then that `None` is return back to the callback.

And with that list, we format it into a response message and publish it to the response topic that was built by NATS under
the hood.


### Request message
```
{
    'request_id': 123, 
    'body:{
            'ticket_id': 123, #Optional
            'client_id': 85940,
            'category': 'SD-WAN',
            'ticket_topic': 'VOO'
            'ticket_status': ['New', 'InProgress'],
    } 
}
```

### Response message
```
{
    'request_id': msg_dict['request_id'],
    'body': All tickets recieved from bruin client,
    'status': 200
}

```
# Get Tickets Details
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.details.request` it makes a callback
to function `send_ticket_details`.  From the request message we obtain the `ticket_id` of the ticket that we want the details
from. 

Using that `ticket_id` as a parameter we make a call to the bruin repository which calls to the bruin client to receive 
a list of details pertaining to the associated `ticket_id`. Now that we have the list we format it into a response message 
and publish it to the response topic that was built by NATS under the hood.


### Request message
```
{
    'request_id': 123,
    'body': {
             'ticket_id': 123,
            }
}
```
### Response message
```
{
    'request_id': msg_dict['request_id'],
    'body': List of ticket details,
    'status': 200
}
```
# Get Tickets Details by edge serial
### Description
When the bruin bridge receives a request with a request message from topic 
`bruin.ticket.affecting.details.by_edge_serial.request` or  `bruin.ticket.outage.details.by_edge_serial.request`
it makes a callback to either the function `send_affecting_ticket_details_by_edge_serial` or 
`send_outage_ticket_details_by_edge_serial`.  From the request message we obtain the `edge_serial` and `client_id` 
of the edge that we want the ticket details from. 

Using that `edge_serial` and `client_id`  as a parameter we make a call to the bruin repository which calls to the bruin client to receive 
a list of details pertaining to the associated `edge_serial` and `client_id` . Now that we have the list we format it into a response message 
and publish it to the response topic that was built by NATS under the hood.


### Request message
```
{
    'request_id': 123,
    'body': {
             'client_id': 123,
              'edge_serial': "VC0123"
              'ticket_statuses':[List of statuses] //optional parameter for bruin.ticket.outage.details.by_edge_serial.request
            }
}
```
### Response message
```
{
    'request_id': msg_dict['request_id'],
    'body': List of ticket details,
    'status': 200
}
```
# Post notes to Ticket
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.note.append.request` it makes a callback
to function `post_note`. From the request message, we need the `ticket_id` to know what ticket to append the note to and 
we need the `note` field for what note to append.

We call the bruin repository with these fields so that it can call the bruin client to post the note to the ticket.
The bruin client should return some success message indicating that our note was successfully posted to the ticket of `ticket_id`.
And then a response message is published to the response topic that was built by NATS under the hood.

### Request message
```
{
    'request_id': 123,
    'body':{
            'ticket_id': 123,
            'note': `Some Ticket Note`
            }
        
}
```
### Response message
```
{
    'request_id': msg_dict['request_id'],
    'body': 'Some response',
    'status': 200
}
```

# Post Ticket
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.creation.request` it makes a callback
to the function `post_ticket`. From the request message, we need the `clientId` to know what client we're creating the ticket for, 
the `category` field for whether its a service affecting ticket (`VAS`) or service outage ticket (`VOO`), `services` field which
is essential the serial number of the edge we're creating the ticket for, and the `contact` field
which is the `email`, `phone number`, and `name` of the ticket's contact.  

We call the bruin repository with these fields so that it can call the bruin client to create the ticket status.
The bruin client should return some success message indicating that our ticket status was successfully changed along with
the ticket id of the newly created ticket.And then a response message is published to the response topic that was built by NATS under the
hood
### Request message
Service Affecting
```
{
    "request_id": 123,
    "body":{
                "clientId": 321,
                "category": "VAS",
                "services": [
                    {
                        "serviceNumber": Serial Number
                    }
                ],
                "contacts": [
                    {
                        "email": "Email@email.com",
                        "phone": "5108324567",
                        "name": "Sample name",
                        "type": "site"
                    },
                    {
                       "email": "Email@email.com",
                       "phone": "5108324567",
                       "name": "Sample name",
                       "type": "ticket"
                    }
                ]
              }
}
```
Service Outage
```
{
    "request_id": 123,
     "body":{
                "clientId": 321,
                "category": "VOO",
                "services": [
                    {
                        "serviceNumber": Serial Number
                    }
                ],
                "contacts": [
                    {
                        "email": "Email@email.com",
                        "phone": "5108324567",
                        "name": "Sample name",
                        "type": "site"
                    },
                    {
                       "email": "Email@email.com",
                       "phone": "5108324567",
                       "name": "Sample name",
                       "type": "ticket"
                    }
                ]
    }
}
```
### Response message
```
{
    'request_id': 123,
    'body': 321,
    'status': 200
}
```

# Open Ticket 
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.status.open` it makes a callback
to the function `open_ticket`. From the request message, we need the `ticket_id` to know what ticket status we need to update, 
aswell as the `detail_id` field.

We call the bruin repository with these fields so that it can call the bruin client to set the ticket status to `open`.
The bruin client should return some success message indicating that our ticket status was successfully changed.
And then a response message is published to the response topic that was built by NATS under the hood.
### Request message
```
{
    'request_id': 123,
    'body':{
            'ticket_id': 321,
            'detail_id': 123
           }
}
```
### Response message
```
{
    'request_id': 123,
    'body': Some response,
    'status': 200
}
```
# Resolve Ticket 
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.status.resolve` it makes a callback
to the function `resolve_ticket`. From the request message, we need the `ticket_id` to know what ticket status we need to update, 
aswell as the `detail_id` field.

We call the bruin repository with these fields so that it can call the bruin client to set the ticket status to `resolve`.
The bruin client should return some success message indicating that our ticket status was successfully changed.
And then a response message is published to the response topic that was built by NATS under the hood.
### Request message
```
{
    'request_id': 123,
    'body':{
            'ticket_id': 321,
            'detail_id': 123
           }

}
```
### Response message
```
{
    'request_id': 123,
    'body': Some response,
    'status': 200
}
```

# Get Management Status 
### Description
When the bruin bridge receives a request with a request message from topic `bruin.inventory.management.status` it will make
a call to the endpoint `/api/Inventory/Attribute` in bruin, using as query params the filters passed in the message.
**NOTE: the filters are passed in snake_case and will be converted to PascalCase before being sent to Bruin's API. client_id filter is MANDATORY**

### Request message
```
{
    'request_id': 123,
    'body': {"client_id": 191919 # MANDATORY parameter,
                "status": "A" # MANDATORY Can be A(Active), D(Decomissined), S(Suspended),
                "service_number": "VCO128739819" # MANDATORY Is the serial number in velocloud
    }

}
```
### Response message
```
{
    'request_id': 123,
    'body':"Active – Platinum Monitoring",
    'status': 200
}

```

# Post Outage Ticket
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.creation.outage.request` it makes a callback
to the function `post_outage_ticket`. From the request message, we need the `client_id` to know what client we're creating the ticket for,
and the `service_number` field which is the serial number of the edge we're creating the outage ticket for.

We call the bruin repository with these fields so that it can call the bruin client to create the outage ticket status.
The bruin client should return some success message indicating that our ticket status was successfully changed along with
the ticket id of the newly created ticket. And then a response message is published to the response topic that was built by NATS under the
hood
### Request message
```
{
    "request_id": 123,
    "client_id": 9994,
    "service_number": "VC05400002265"
}
```

### Response message
```
{
    'request_id': 123,
    'body': 123456,  # Ticket ID
    'status': 200
}
```

# Running in docker-compose 
`docker-compose up --build redis nats-server bruin-bridge`