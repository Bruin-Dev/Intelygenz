# Scripts

This folder contains some scripts used as tools for solving issues when on call.

**Table of content:**

+ [Common on-call requests](#common-on-call)
+ [Autoresolve tickets](#autoresolve_tickets)
    - [Description](#autoresolve_tickets_description)
    - [Usage](#autoresolve_tickets_usage)

## Common on-call requests

Please refer to the [on-call playbook](docs/ON-CALL%20PLAYBOOK.md)

## Autoresolve ticekts <a name="autoresolve_tickets"></a>

### Description <a name="autoresolve_tickets_description"></a>

The Python [script](autoresolve_tickets.py). The script given a ticket id list will try to get the ticket details for each ticket in the list and mark them as resolved.

### Usage <a name="autoresolve_tickets_usage"></a>

Run this sequence of commands to initialize the Poetry virtualenv and install all required dependencies:

```shell
# These commands assume your current working dir is the root of the project
cd scripts/on-call
poetry install
```

Next, edit on the script `autoresolve_tickets.py` the line where the ticket_ids are defined with the one we need to mark as Resolved.

Then run the docker services nats-server and bruin-bridge on local:
```shell
docker-compose up --build nats-server bruin-bridge
```

Finally, run the script with the following command:
```shell
poetry run python autoresolve_tickets.py
```

After completion, the script should have marked all the given ticket as resolved.
