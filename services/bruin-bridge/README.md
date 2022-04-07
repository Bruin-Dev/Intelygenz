
# Bruin bridge
* [Description](#description)
* [Links](#links)
* [Requests](#requests)
  * [Get All Tickets](#get-all-tickets)
  * [Get Tickets Details](#get-tickets-details)
  * [Post notes to Ticket](#post-notes-to-ticket)
  * [Post Ticket](#post-ticket)
  * [Open Ticket](#open-ticket)
  * [Resolve Ticket](#resolve-ticket)
  * [Get Management Status](#get-management-status)
  * [Post Outage Ticket](#post-outage-ticket)
  * [Get Bruin Client Info](#get-bruin-client-info)
  * [Post multiple notes to ticket](#post-multiple-notes-to-ticket)
  * [Get next results for ticket detail](#get-next-results-for-ticket-detail)
  * [Get ticket overview](#get-ticket-overview)
  * [Get ticket task history](#get-ticket-task-history)
  * [Get circuit id](#get-circuit-id)
  * [Get Site](#get-site)
  * [Get Attributes Serial](#get-attributes-serial)
* [Running in docker-compose](#running-in-docker-compose)

# Description
Bruin Bridge is used to make calls to the Bruin API. The main calls include [getting all tickets](#get-all-tickets), [getting ticket details](#get-tickets-details),
[appending notes to tickets](#post-notes-to-ticket), and creating tickets.

![IMAGE: bruin-bridge_microservice_relationships](/docs/img/system_overview/capabilities/bruin-bridge_microservice_relationships.png)

# Links
- Bruin app: https://app.bruin.com
- Bruin swagger: https://api.bruin.com/index.html

# Requests
## Get All Tickets
When the bruin bridge receives a request with a request message from topic `bruin.ticket.request` it makes a callback
to function `get_all_tickets`.  The request message, contains all of the fields needed to filter the tickets and
receive only relevant tickets. These fields include `ticket_id`, `client_id`, `service_number`, `ticket_status`, and `category`. 
Once all of the fields are extracted from the request message, a call to the bruin repository is made.

In the bruin repository, it loops through the `ticket_status` field which should be a list. Each time it will make
a call to the bruin client to receive all the tickets matching the filter. At the end of the loop, all the tickets returned
from the bruin clients for each status should be combined into one big list of tickets. Which gets sent back to the callback
function. If any of the tickets received from bruin client return `None` then that `None` is return back to the callback.

And with that list, we format it into a response message and publish it to the response topic that was built by NATS under
the hood.

```python
request_message = {
    'request_id': 'kNxC7FxXpg5ApdgGaX7otC',  # UUID
    'body': {
        'ticket_id': 123,  # Optional
        'service_number': 'VC05400002265',  # Optional
        'client_id': 85940,
        'category': 'SD-WAN',
        'ticket_topic': 'VOO',
        'ticket_status': ['New', 'InProgress'],
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': [], # All tickets recieved from bruin client
    'status': 200,
}
```

## Get Tickets Details
When the bruin bridge receives a request with a request message from topic `bruin.ticket.details.request` it makes a callback
to function `send_ticket_details`.  From the request message we obtain the `ticket_id` of the ticket that we want the details
from. 

Using that `ticket_id` as a parameter we make a call to the bruin repository which calls to the bruin client to receive 
a list of details pertaining to the associated `ticket_id`. Now that we have the list we format it into a response message 
and publish it to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'body': {
        'ticket_id': 123,
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': [], # List of ticket details
    'status': 200,
}
```

## Post notes to Ticket
When the bruin bridge receives a request with a request message from topic `bruin.ticket.note.append.request` it makes a callback
to function `post_note`. From the request message, we need the `ticket_id` to know what ticket to append the note to and 
we need the `note` field for what note to append.

We call the bruin repository with these fields so that it can call the bruin client to post the note to the ticket.
The bruin client should return some success message indicating that our note was successfully posted to the ticket of `ticket_id`.
And then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'body': {
        'ticket_id': 123,
        'note': "Some Ticket Note",
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': 'Some response',
    'status': 200,
}
```

## Post Ticket
When the bruin bridge receives a request with a request message from topic `bruin.ticket.creation.request` it makes a callback
to the function `post_ticket`. From the request message, we need the `clientId` to know what client we're creating the ticket for, 
the `category` field for whether its a service affecting ticket (`VAS`) or service outage ticket (`VOO`), `services` field which
is essential the serial number of the edge we're creating the ticket for, and the `contact` field
which is the `email`, `phone number`, and `name` of the ticket's contact.

> Although this topic is able to create outage tickets, you should use a topic specifically designed for this.
> See [this section](#post-outage-ticket) for more details on how to use it.

We call the bruin repository with these fields so that it can call the bruin client to create the ticket status.
The bruin client should return some success message indicating that our ticket status was successfully changed along with
the ticket id of the newly created ticket.And then a response message is published to the response topic that was built by NATS under the
hood

```python
request_message = {
    'request_id': 123,
    'body': {
        'clientId': 321,
        'category': '[VAS|VOO]', # VAS: affecting service, VOO: outage
        'services': [
            {
                'serviceNumber': '', # Serial Number
            },
        ],
        'contacts': [
            {
                'email': 'Email@email.com',
                'phone': '5108324567',
                'name': 'Sample name',
                'type': 'site',
            },
            {
               'email': 'Email@email.com',
               'phone': '5108324567',
               'name': 'Sample name',
               'type': 'ticket',
            },
        ],
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': 321,
    'status': 200,
}
```

## Open Ticket 
When the bruin bridge receives a request with a request message from topic `bruin.ticket.status.open` it makes a callback
to the function `open_ticket`. From the request message, we need the `ticket_id` to know what ticket status we need to update, 
aswell as the `detail_id` field.

We call the bruin repository with these fields so that it can call the bruin client to set the ticket status to `open`.
The bruin client should return some success message indicating that our ticket status was successfully changed.
And then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'body': {
        'ticket_id': 321,
        'detail_id': 123,
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': 'Some response',
    'status': 200,
}
```

## Resolve Ticket 
When the bruin bridge receives a request with a request message from topic `bruin.ticket.status.resolve` it makes a callback
to the function `resolve_ticket`. From the request message, we need the `ticket_id` to know what ticket status we need to update, 
aswell as the `detail_id` field.

We call the bruin repository with these fields so that it can call the bruin client to set the ticket status to `resolve`.
The bruin client should return some success message indicating that our ticket status was successfully changed.
And then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'body': {
        'ticket_id': 321,
        'detail_id': 123,
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': 'Some response',
    'status': 200,
}
```

## Get Management Status 
When the bruin bridge receives a request with a request message from topic `bruin.inventory.management.status` it will make
a call to the endpoint `/api/Inventory/Attribute` in bruin, using as query params the filters passed in the message.
**NOTE: the filters are passed in snake_case and will be converted to PascalCase before being sent to Bruin's API. client_id filter is MANDATORY**

```python
request_message = {
    'request_id': 123,
    'body': {
        "client_id": 191919, # MANDATORY parameter,
        "status": "A", # MANDATORY Can be A(Active), D(Decomissined), S(Suspended),
        "service_number": "VCO128739819", # MANDATORY Is the serial number in velocloud
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body':"Active – Platinum Monitoring",
    'status': 200,
}
```

## Post Outage Ticket
When the bruin bridge receives a request with a request message from topic `bruin.ticket.creation.outage.request` it makes a callback
to the function `post_outage_ticket`. From the request message, we need the `client_id` to know what client we're creating the ticket for,
and the `service_number` field which is the serial number of the edge we're creating the outage ticket for.

We call the bruin repository with these fields so that it can call the bruin client to create the outage ticket status.
The bruin client should return some success message indicating that our ticket status was successfully changed along with
the ticket id of the newly created ticket. And then a response message is published to the response topic that was built by NATS under the
hood

```python
request_message = {
    'request_id': 123,
    'client_id': 9994,
    'service_number': 'VC05400002265',
}

response_message = {
    'request_id': request_message['request_id'],
    'body': 123456, # Ticket ID
    'status': 200,
}
```

## Get Bruin Client Info
When the bruin bridge receives a request with a request message from topic `bruin.customer.get.info` it makes a callback
to the function `get_client_info`. From the request message, we need the `service_number` to know who is the customer owning
the corresponding edge based on Bruin's inventory data.

We call the bruin repository with these fields so that it can call the bruin client to get the client info.
The bruin client should return a message contanining the information of the customer that the service number belongs to.

```python
request_message = {
    'request_id': 123,
    'service_number': 'VC05400002265',
}

response_message = {
    'request_id': request_message['request_id'],
    'body': {
        'client_id': 9994,
        'client_name': 'METTEL/NEW YORK',
        'site_id': 1234,
    },
    'status': 200,
}
```

## Post multiple notes to ticket
When the bruin bridge receives a request with a request message from topic `bruin.ticket.multiple.notes.append.request` it makes a callback
to function `post_multiple_notes`. From the request message, we need the `ticket_id` to know what ticket to append the notes to and 
we need the list of notes under a field called `notes`. Each note must have the `text` field, which is the content of the note, and
at least the field `service_number` or `detail_id` (can have both).

We call the bruin repository with these fields so that it can call the bruin client to post the notes to the ticket.
The bruin client should return some success message indicating that our notes were successfully posted to the ticket of `ticket_id`.
And then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'ticket_id': 12345,
    'notes': [
        {
            'text': 'Note contents',
            'service_number': 'VC123457',
            'detail_id': 99999,
        },
    ],
}

response_message = {
    'request_id': request_message['request_id'],
    'body': [
        {
            'noteID': 12345,
            'noteType': 'ADN',
            'noteValue': 'Note contents',
            'detailID': 99999,
        },
    ],
    'status': 200,
}
```

## Get next results for ticket detail
When the bruin bridge receives a request with a request message from topic `bruin.ticket.detail.get.next.results` it makes a callback
to function `get_next_results_for_ticket_detail`. From the request message, we need the `ticket_id`, `detail_id` and `service_number` to know
the next results available for the detail / service number under the ticket specified.

> _Results_ refer to states a detail / service number can be on in the context of the resolution of the issue it addresses.

We call the bruin repository with these fields so that it can call the bruin client to get the list of next results.
The bruin client should return a message having the list of next results for the detail / service number of the ticket.
And then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'ticket_id': 12345,
    'detail_id': 99999,
    'service_number': 'VC123457',
}

response_message = {
    'request_id': request_message['request_id'],
    'body': [
        {
            'resultTypeId': 620,
            'resultName': 'No Trouble Found - Carrier Issue',
        },
    ],
    'status': 200,
}
```

## Get ticket overview
When the bruin bridge receives a request with a request message from topic `bruin.ticket.overview.request` it makes a callback
to function `get_ticket_overview`. From the request message, we need the `ticket_id` to know its overview info.

We call the bruin repository with these fields so that it can call the bruin client to get the overview of the ticket.
The bruin client should return a message having that overview, and then a response message is published to the response topic
that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'ticket_id': 12345,
}

response_message = {
    'request_id': request_message['request_id'],
    'body': {
        'clientID': 9994,
        'clientName': 'METTEL/NEW YORK',
        'ticketID': 12345,
        'topic': 'VAS',
        'ticketStatus': 'InProgress',
        'address': {
            'address': 'Fake Street 123',
            'city': 'Newark',
            'state': 'NJ',
            'zip': '12345-6789',
            'country': 'USA'
        },
        'createDate': '4/23/2019 7:59:50 PM',
    },
    'status': 200,
}
```

## Get ticket task history
When the bruin bridge receives a request with a request message from topic `bruin.ticket.get.task.history` it makes a callback
to function `get_ticket_task_history`. From the request message, we need the `ticket_id` to know the history of the ticket

> The history of a ticket is a list where each element corresponds to an event related to that ticket. An example of an event is appending
> a note, changing the status of the ticket...

We call the bruin repository with these fields so that it can call the bruin client to get the history of the ticket.
The bruin client should return a message having that history, and then a response message is published to the response topic
that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'ticket_id': 12345,
}

response_message = {
    'request_id': request_message['request_id'],
    'body': [
        {
          'ClientName': 'METTEL/NEW YORK',
          'Ticket Entered Date': '202010292252',
          'EnteredDate': '2020-10-29T22:52:49.22-04:00',
          'CallTicketID': 4906680,
          'Initial Note @ Ticket Creation': 'Automation Engine -- Service Outage Trouble',
          'DetailID': None,
          'Product': None,
          'Asset': None,
          'Address1': 'Fake Street 123',
          'Address2': None,
          'City': 'Rapture',
          'State': 'NY',
          'Zip': '12345-6789',
          'Site Name': 'Some pretty cool place',
          'NoteType': 'ADN',
          'Notes': 'Request Description: Automation Engine -- Service Outage Trouble\n',
          'Note Entered Date': '202010292252',
          'EnteredDate_N': '2020-10-29T22:52:51.063-04:00',
          'Note Entered By': 'Travis Touchdown',
          'Task Assigned To': None,
          'Task': None,
          'Task Result': None,
          'SLA': None,
          'Ticket Status': 'Closed',
       },
    ],
    'status': 200,
}
```

## Get Circuit Id
When the bruin bridge receives a request with a request message from topic `bruin.get.circuit.id` it makes a callback
to function `get_circuit_id`. From the request message, we need the `circuit_id` and `client_id` to get the circuit id
dict from bruin.

We call the bruin repository with these fields so that it can call the bruin client to get the circuit id dict from bruin.
The bruin client should return a message having the circuit id(`wtn` is the field name in the dict) along with other fields,
and then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'body': {
        'circuit_id': 'DS1IT-22880336',
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': {
        'clientID': 83959,
        'subAccount': 'string',
        'wtn': '3214',
        'inventoryID': 0,
        'addressID': 0,
    },
    'status': 200,
}
```

## Get Site
When the bruin bridge receives a request with a request message from topic `"bruin.get.site"` it makes a callback
to function `get_site`. From the request message, we need the `site_id` and `client_id` to get the details of a site
for a particular client from Bruin.

We call the bruin repository with these fields so that it can call the bruin client to get the site details dict from bruin.
The bruin client should return a message having the site details like the site's contact info along with other fields,
and then a response message is published to the response topic that was built by NATS under the hood.

```python
request_message = {
    'request_id': 123,
    'body': {
        'client_id': 85719,
        'site_id': 999,
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': [
        {
            'clientID': 85719,
            'clientName': 'Rotech Healthcare, Inc.',
            'siteID': 999,
            'siteLabel': '4074320248 - DEBORAH ROBERTSON',
            'siteAddDate': '2016-10-06T15:32:23.897Z',
            'address': {
                'addressID': 1675311,
                'address': '3600 Vineland Rd Ste 114',
                'city': 'Orlando',
                'state': 'FL',
                'zip': '32811-6460',
                'country': 'USA'
            },
            'longitude': -81.429743,
            'latitude': 28.5047608,
            'businessHours': 'SUNDAY|NOT AVAILABLE,MONDAY|8PM-6PM,TUESDAY|8PM-6PM,WEDNESDAY|8PM-6PM,THURSDAY|8PM-6PM,FRIDAY|8PM-6PM,SATURDAY|NOT AVAILABLE',
            'timeZone': 'Eastern',
            'primaryContactName': 'Help Desk',
            'primaryContactPhone': None,
            'primaryContactEmail': 'test@email.com',
        },
    ],
    'status': 200,
}
```

## Get Attributes Serial 
When the bruin bridge receives a request with a request message from topic `bruin.inventory.attributes.serial` it will make
a call to the endpoint `/api/Inventory/Attribute` in bruin, using as query params the filters passed in the message.
**NOTE: the filters are passed in snake_case and will be converted to PascalCase before being sent to Bruin's API. client_id filter is MANDATORY**

```python
request_message = {
    'request_id': 123,
    'body': {
        'client_id': 89267, # MANDATORY parameter,
        'status': 'A', # MANDATORY Can be A(Active), D(Decomissined), S(Suspended),
        'service_number': '5006950173', # MANDATORY Is the serial number or something similar (i.e circuit id)
    },
}

response_message = {
    'request_id': request_message['request_id'],
    'body': '705286',
    'status': 200,
}

```

# Running in docker-compose 
`docker-compose up --build redis nats-server bruin-bridge`
