# Ticket severity

## Process Workflows

![](../../images/6-tickets-severity.png)

## List of Decisions made by ticket severity

### Ticket Severity

#### Start of change ticket severity

|                                  |                              |                          |
|----------------------------------|------------------------------|--------------------------|
| 1. Outage condition is detected  | Edge DOWN                    | Link DOWN                |

##### Edge Down
|                                                    |                                |
|----------------------------------------------------|--------------------------------|
| 1. Attempt to create a service Outage bruin ticket | Status 200, 409, 473, 472, 471 |
| 2. Set ticket severity 2                           | END                            |

##### Link Down
|                                                    |                                        |                                     |
|----------------------------------------------------|----------------------------------------|-------------------------------------|
| 1. Attempt to create a service Outage bruin ticket | Status 200 or 473                      | Status 409, 472 or 471              |
| 2. For status 200 or 473                           | Set ticket severity 3                  | -                                   |
| 3. For status 409, 472 or 471                      | Ticket with only 1 Task set severity 3 | If ticket have more than 1 task end |


#### Autoresolution
## Event Descriptions
* [Attempt ticket creation ](../services/service-outage-monitor/actions/outage_monitoring/_attempt_ticket_creation.md)