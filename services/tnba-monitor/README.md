# Table of contents
  * [Description](#description)
  * [Work Flow](#work-flow)
  * [Behaviour in dev and in pro](#behaviour-in-development-and-in-production)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The TNBA monitor is currently used to monitor all the tickets created for Bruin clients that are relevant
for the Automation Engine, and to attach to them TNBA notes when needed. These notes contain a prediction
indicating what is **T**he **N**ext **B**est **A**ction a member from the support team of Bruin can take to
move forward on the resolution of the ticket.

# Work Flow
First of all, the process claims the cache of customers for the Velocloud host(s) specified in the config file
of this service.

After that, the process claims all open tickets belonging to clients included in the cache, along with their
details and notes, from Bruin. Before moving on, the process discards irrelevant tickets, details and notes.

After claiming the set of tickets, the process splits this set into two: tickets with one or more TNBA notes and
tickets without TNBA notes. The process then runs two tasks to deal with both sets of tickets simultaneously.

### Processing tickets with at least one TNBA note
Every time one of these tickets is processed, a request is sent to T7 API. The response contains
a list of predictions grouped by serial number, and each prediction has a list of actions and probabilities.
Every probability points out how good it is to take that action; the higher the probability is, the better
that action will be to move forward on the resolution of the ticket.

A ticket can have several details, so they all are processed separately. Note that a detail is always
bound to a single serial number in the context of a ticket.

A detail is taken into account only if:
- The latest TNBA note related to the serial was not appended too recently (30 minutes ago).
- There is a prediction for that ticket in the response that came from T7 API at the beginning of the process.
- The prediction found for this serial has any of the actions as pointed out by Bruin API. This check is
  performed after asking for the next available actions for the detail.
- The best action changed since the last TNBA note for this detail.

If all of these conditions are met, the process builds a TNBA note for that serial number.
The note is then appended to the ticket along with all the TNBA notes built in subsequent details, but only
if the environment is `PRODUCTION`. If the environment is `DEV`,  the note is simply delivered
as a Slack notification; no real action over Bruin is taken.

#### Processing tickets without TNBA notes
Every time one of these tickets is processed, a request is sent to T7 API. The response contains
a list of predictions grouped by serial number, and each prediction has a list of actions and probabilities.
Every probability points out how good it is to take that action; the higher the probability is, the better
that action will be to move forward on the resolution of the ticket.

A ticket can have several details, so they all are processed separately. Note that a detail is always
bound to a single serial number in the context of a ticket.

A detail is taken into account only if:
- There is a prediction for that ticket in the response that came from T7 API at the beginning of the process.
- The prediction found for this serial has any of the actions as pointed out by Bruin API. This check is
  performed after asking for the next available actions for the detail.

If all of these conditions are met, the process builds a TNBA note for that serial number.
The note is then appended to the ticket along with all the TNBA notes built in subsequent details, but only
if the environment is `PRODUCTION`. If the environment is `DEV`,  the note is simply delivered
as a Slack notification.

# Capabilities used
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifications bridge](../notifications-bridge/README.md)
- [T7 bridge](../t7-bridge/README.md)
- [Velocloud bridge](../velocloud-bridge/README.md)

# Running in docker-compose
`docker-compose up --build redis nats-server bruin-bridge velocloud-bridge t7-bridge notifications-bridge tnba-monitor`
