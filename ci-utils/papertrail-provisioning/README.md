# Papertrail provisioning

In this folder are the utilities to perform the papertrail provisioning for the different microservices of the project in each environment, **although for the time being it will only be used in the production environment**.

## Usage

This utility is intended to be used in the gitlab deployment pipelines for each environment, it uses a configuration file called [config.py](./config.py) where it will collect the different environment variables needed.

Papertrail is organized in [groups](https://help.papertrailapp.com/kb/how-it-works/groups/), elements where one or more [searches]() are defined.

It is possible to add and/or remove papertrail groups, as well as the searches on them by means of the mentioned config.py file, through the modification of the dictionary value named `PAPERTRAIL_PROVISIONING`. The following should be noted about this element:

- In this element a group arrays dictionary is defined, where the name of the group must be defined in each case, as well as the searches to be carried out in this one by means of another dictionary, indicating for these last ones the name and the query of the same ones.

- Certain environment variables are used to make available the logs of the last deployment of each microservice, using these to update the queries of the previously existing searches of each microservice.

- It is also possible to define groups with searches that will be used to send notifications and/or alarms, these will be distinguished from the others since it will not be necessary to update them to obtain the latest deployments of each microservice.

## Example of Usage

### Group with searches for logs of each microservice

Below is the configuration of the `PAPERTRAIL_PROVISIONING` element mentioned in the previous section, defining a group with a search for each of the microservices, as well as one for all the microservices.

```
{
    "groups": [
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} logs",
            "searches": [
                {
                    "query": f"bruin-bridge AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[bruin-bridge] - logs"
                },
                {
                    "query": f"cts-bridge AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[cts-bridge] - logs"
                },
                {
                    "query": f"dispatch-portal-backend AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[dispatch-portal-backend] - logs"
                },
                {
                    "query": f"grafana AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[grafana] - logs"
                },
                {
                    "query": f"last-contact-report AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[last-contact-report] - logs"
                },
                {
                    "query": f"lit-bridge AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[lit-bridge] - logs"
                },
                {
                    "query": f"lumin-billing-report AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[lumin-billing-report] - logs"
                },
                {
                    "query": f"service-affecting-monitor AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-affecting-monitor] - logs"
                },
                {
                    "query": f"service-dispatch-monitor AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-dispatch-monitor] - logs"
                },
                {
                    "query": f"service-outage-monitor-1 AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-outage-monitor-1] - logs"
                },
                {
                    "query": f"service-outage-monitor-2 AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-outage-monitor-2] - logs"
                },
                {
                    "query": f"service-outage-monitor-3 AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-outage-monitor-3] - logs"
                },
                {
                    "query": f"service-outage-monitor-4 AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-outage-monitor-4] - logs"
                },
                {
                    "query": f"service-outage-monitor-triage AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[service-outage-monitor-triage] - logs"
                },
                {
                    "query": f"sites-monitor AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[sites-monitor] - logs"
                },
                {
                    "query": f"t7-bridge AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[t7-bridge] - logs"
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[tnba-monitor] - logs"
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[velocloud-bridge] - logs"
                },
                {
                    "query": f"{ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[all modules] - logs",
                }
            ]
        }
```

### Group with searches for alarms and notifications

Below is the configuration of the `PAPERTRAIL_PROVISIONING` element mentioned in the previous section, defining groups for notifications and alarms, with specific searches for each one.

```
"groups": [
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} notifications",
            "notifications": True,
            "searches": [
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                             f"\"Successfully created outage ticket for edge\"",
                    "search_name": f"[service-outage-monitor] - ticket creation"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                             f"\"Ticket linked to edge was autoresolved!\"",
                    "search_name": f"[service-outage-monitor] - ticked autoresolved"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                             f"\"Triage appended to detail\"",
                    "search_name": f"[service-outage-monitor] - triage appended"
                }
            ]
        },
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} alarms",
            "alarms": True,
            "searches": [
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                             f"\"Successfully created outage ticket for edge\"",
                    "search_name": f"[service-outage-monitor] - ticket creation"
                }
            ]
        }
    ]
}
```
