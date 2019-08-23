# Table of contents
  * [Bruin API](#bruin-api)
    * [Description](#description)
    * [Links](#links)
  * [Work queues]()
    * [Get All Tickets](#get-all-tickets)
        * [Description](#description-1)
        * [Request message](#request-message)
        * [Response message](#response-message)
    * [Get Tickets Details](#get-tickets-details)
        * [Description](#description-2)
        * [Request message](#request-message-1)
        * [Response message](#response-message-1)
    * [Post notes to Ticket](#post-notes-to-ticket)
        * [Description](#description-3)
        * [Request message](#request-message-2)
        * [Response message](#response-message-2)
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

And with that list, we format it into a response message and publish it to the response topic provided by the request message.


### Request message
```
{
    'request_id': 123, 
    'response_topic': f'bruin.ticket.response.{service_id}',
    'ticket_id': 123
    'client_id': 85940, 
    'ticket_status': ['New', 'InProgress'], 
    'category': 'SD-WAN'
}
```

### Response message
```
{
    'request_id': msg_dict['request_id'],
    'tickets': All tickets recieved from bruin client,
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
and publish it to the response topic provided in the request message. 


### Request message
```
{
    'request_id': 123,
    'response_topic': f'bruin.ticket.details.response.{service_id}',
    'ticket_id': 123}
}
```
### Response message
```
{
    'request_id': msg_dict['request_id'],
    'ticket_details': List of ticket details,
    'status': 200
}
```
# Post notes to Ticket
### Description
When the bruin bridge receives a request with a request message from topic `bruin.ticket.note.append.request` it makes a callback
to function `post_note`. From the request message, we need the `ticket_id` to know what ticket to append the note to and 
we need the `note` field for what note to append.

We call the bruin repository with these fields so that it can call the bruin client to post the note to the ticket.
The bruin client should return some success message indicating that our note was successfuly posted to the ticket of `ticket_id`.
And then a response message is publish to the response topic provided by the request message.

### Request message
```
{
    'request_id': 123,
    'response_topic': f'bruin.ticket.note.append.response.{service_id}',
    'ticket_id': 123
    'note': `Some Ticket Note`
}
```
### Response message
```
{
    'request_id': msg_dict['request_id'],
    'status': 200
}
```
    