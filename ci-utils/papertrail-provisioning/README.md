# Papertrail provisioning

In this folder are the utilities to perform the papertrail provisioning for the different microservices of the project in each environment, **although for the time being it will only be used in the production environment**.

## Usage

This utility is intended to be used in the gitlab deployment pipelines for each environment, it uses a configuration file called [config.py](./config.py) where it will collect the different environment variables needed.

Papertrail is organized in [groups](https://help.papertrailapp.com/kb/how-it-works/groups/), elements where one or more [searches]() are defined.

It is possible to add and/or remove papertrail groups, as well as the searches on them by means of the mentioned config.py file, through the modification of the dictionary value named `PAPERTRAIL_PROVISIONING`. The following should be noted about this element:

- In this element a group arrays dictionary is defined, where the name of the group must be defined in each case, as well as the searches to be carried out in this one by means of another dictionary, indicating for these last ones the name and the query of the same ones.

  **In the case of adding the search on logs of a microservice, the ECR repository must be added where the images of the microservice are stored, using the `repository` key in the dictionary.**

- It is also possible to define groups with searches that will be used to send notifications and/or alarms, these will be distinguished from the others since it will not be necessary to update them to obtain the latest deployments of each microservice.

## Example of Usage

### Group with searches for logs of each microservice

Below is the configuration of the `PAPERTRAIL_PROVISIONING` element mentioned in the previous section, defining a group with a search for each of the microservices, as well as one for all the microservices.

```
"groups": [
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} logs",
            "searches": [
                {
                    "query": f"bruin-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[bruin-bridge] - logs",
                    "repository": "automation-bruin-bridge"
                },
                {
                    "query": f"cts-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[cts-bridge] - logs",
                    "repository": "automation-cts-bridge"
                },
                {
                    "query": f"customer-cache AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[customer-cache] - logs",
                    "repository": "automation-customer-cache"
                },
                {
                    "query": f"dispatch-portal-backend AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[dispatch-portal-backend] - logs",
                    "repository": "automation-dispatch-portal-frontend"
                },
                {
                    "query": f"dispatch-portal-backend AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[dispatch-portal-backend] - logs"
                },
                {
                    "query": f"hawkeye-bridge AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[hawkeye-bridge] - logs"
                },
                {
                    "query": f"hawkeye-customer-cache AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[hawkeye-customer-cache] - logs"
                },
                {
                    "query": f"hawkeye-outage-monitor AND {ENVIRONMENT_NAME} AND {BUILD_NUMBER}",
                    "search_name": f"[hawkeye-outage-monitor] - logs"
                },
                {
                    "query": f"last-contact-report AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[last-contact-report] - logs",
                    "repository": "automation-last-contact-report"
                },
                {
                    "query": f"lit-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[lit-bridge] - logs",
                    "repository": "automation-lit-bridge"
                },
                {
                    "query": f"lumin-billing-report AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[lumin-billing-report] - logs",
                    "repository": "automation-lumin-billing-report"
                },
                {
                    "query": f"NGINX AND <BUILD_NUMBER> AND {ENVIRONMENT_ID}",
                    "search_name": f"[nginx] - logs",
                    "repository": "automation-dispatch-portal-frontend/nginx"
                },
                {
                    "query": f"service-affecting-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-affecting-monitor] - logs",
                    "repository": "automation-service-affecting-monitor"
                },
                {
                    "query": f"service-dispatch-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-dispatch-monitor] - logs",
                    "repository": "automation-service-dispatch-monitor"
                },
                {
                    "query": f"service-outage-monitor-1 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-1] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-2 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-2] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-3 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-3] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-4 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-4] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-triage AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-triage] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"t7-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[t7-bridge] - logs",
                    "repository": "automation-t7-bridge"
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-monitor] - logs",
                    "repository": "automation-tnba-monitor"
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-feedback] - logs",
                    "repository": "automation-tnba-feedback"
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[velocloud-bridge] - logs",
                    "repository": "automation-velocloud-bridge"
                },
                {
                    "query": f"{ENVIRONMENT_ID}",
                    "search_name": f"[all modules] - logs",
                }
            ]
}
```

> The word `<BUILD_NUMBER>` in the `query` key for each `search` will be replaced for the corresponding value in the deployment process, using the `repository` key and the file with the last docker images updated to the ECR repositories.
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
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Successfully created outage ticket for edge\"",
                    "search_name": f"[service-outage-monitor] - ticket creation"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Ticket linked to edge was autoresolved!\"",
                    "search_name": f"[service-outage-monitor] - ticked autoresolved"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
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
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Successfully created outage ticket for edge\"",
                    "search_name": f"[service-outage-monitor] - ticket creation"
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_ID} AND "
                             f"\"ERROR:\"",
                    "search_name": f"[velocloud-bridge] - ERROR messages"
                },
                {
                    "query": f"bruin-bridge AND {ENVIRONMENT_ID} AND "
                             f"\"ERROR:\"",
                    "search_name": f"[bruin-bridge] - ERROR messages"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"ERROR:\"",
                    "search_name": f"[service-outage-monitor] - ERROR messages"
                }
            ]
        }
    ]
}
```
