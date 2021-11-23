# Table of contents
  * [Description](#description)
  * [Workflow](#work-flow)
  * [Ticket Notes](#ticket-notes)
  * [Capabilities used](#capabilities-used)
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The `bouncing-detector` job is to monitor all edges every 30 mins and looks for any circuit instability. A circuit instability
is defined through any bouncing events or 10+ `EDGE_DOWN` or `LINK_DEAD` events occurring within the past hour.
If a circuit instability is found then a service affecting ticket is created if a ticket doesn't already exist. 
If a service affecting ticket exists then it would check to see if the ticket needs to be reopened. 
Regardless if it's a new ticket, reopened ticket, or an already open ticket a circuit instability note is posted to that ticket.

### Work Flow
The class scheduler runs the `_bouncing_detector_process` job every 30 minutes. In this process we obtain the customer_cache
and the link_metrics for later usage. We then reorganize the customer-cache data to be a dict (`enterprise_to_edge_info`) that has `enterprise_id`s
as the key and a list of related cached edges as the value.

We use that newly formed dict to get the past events that happened in the last hour per `enterprise_id`. The events we get should either be `EDGE_DOWN` or `LINK_DEAD` events.
We then will take the `edgeName` of each event events that occurred in that `enterprise_id` and see if matches any of the `edge_name` of the
cached_edges in that `enterprise_id`'s list of edges in the `enterprise_to_edge_info` dict. If it does then we append that
event to a list which will act as the value that will correspond to a key which is defined by the `serial_number` of the edge , and it
all goes into our newly formed dict, `events_by_serial`.

Now that we have a dict with serial numbers to a list of `EDGE_DOWN` or `LINK_DEAD` events, we can easily check for any bouncing events.
If we have 10+ `EDGE_DOWN` we will proceed to make a ticket dict that which will serve as the base for the ticket note.
For links, we have to check the `message` of the event object to determine which interface does the `LINK_DEAD` belong to.
If we have 10+ `LINK_DEAD` for one interface we will proceed to make a ticket dict that which will serve as the base for the ticket note.
Once we have our ticket dicts we are now ready to make a ticket.

Before we make a ticket, we check to see if a service-affecting ticket already exists. 
- If a service-affecting ticket doesn't exist then we create a ticket and format the ticket_dict into a ticket note that gets posted to the newly created ticket.
- If a service-affecting ticket exists and resolved then we reopen the ticket and format the ticket_dict into a reopen ticket note that gets posted to the reopened ticket.
- If a service-affecting ticket exists and not resolved then we format the ticket_dict into ticket note that gets posted to the already open ticket.

### Ticket Notes

Circuit Instability in Edge Note
````
#*MetTel's IPA*#
Trouble: Circuit Instability

Edge Name: OReilly-HotSprings-AR-Store-803
Name: ATT Wireless (MetTel 5773072002)

Interval for Scan: 30
Threshold: 10
Events: 15

Scan Time: 2021-07-28 16:37:28.347957-04:00
Links: Edge  - QoE  - Transport 

````

Circuit Instability in Link Note
````
#*MetTel's IPA*#
Trouble: Circuit Instability

Edge Name: OReilly-HotSprings-AR-Store-803
Name: ATT Wireless (MetTel 5773072002)
Interface: GE1
Link Type: Public Wireless

Interval for Scan: 30
Threshold: 10
Events: 15

Scan Time: 2021-07-28 16:37:28.347957-04:00
Links: Edge  - QoE  - Transport 
````

Circuit Instability in Link Reopen Note
````
#*MetTel's IPA*#
Re-opening ticket.

Trouble: Circuit Instability

Edge Name: OReilly-HotSprings-AR-Store-803
Name: ATT Wireless (MetTel 5773072002)
Interface: GE1
Link Type: Public Wireless

Interval for Scan: 30
Threshold: 10
Events: 15

Scan Time: 2021-07-28 16:37:28.347957-04:00
Links: Edge  - QoE  - Transport 

````



# Capabilities used
- [Customer cache](../customer-cache/README.md)
- [Velocloud bridge](../velocloud-bridge/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)


# Running in docker-compose
- Velocloud host #1 -> `docker-compose up --build nats-server redis velocloud-bridge bruin-bridge notifier customer-cache bouncing-detector-1`
- Velocloud host #2 -> `docker-compose up --build nats-server redis velocloud-bridge bruin-bridge notifier customer-cache bouncing-detector-2`
- Velocloud host #3 -> `docker-compose up --build nats-server redis velocloud-bridge bruin-bridge notifier customer-cache bouncing-detector-3`
- Velocloud host #4 -> `docker-compose up --build nats-server redis velocloud-bridge bruin-bridge notifier customer-cache bouncing-detector-4`
