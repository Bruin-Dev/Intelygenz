# HNOC Forwarding Event Logging

## Process Workflows
![](../../images/3-HNOC-fordwarding.png)

## List of Decisions made by the HNOC forwarding System
### HNOC forwarding queue
#### Start of  HNOC forwarding workflow (SO)

|                                              |                               |                     |
|----------------------------------------------|-------------------------------|---------------------|
| 1. Service outage detected                   |                               |                     |
| 2. Attempt to create ticket outage           | Create new SO ticket          | Reopen exist ticket |
| 3. If exist ticket and have more than 60 min | Forward HNOC                  | END                 |
| 4. New ticket created                        | Append triage note            |                     |
| 5. If edge outage Forward to HNOC            | END                           |                     |
| 6. If link outage                            | Check if more than 60 minutes |                     |

#### Start of  HNOC forwarding workflow (SA)

|                                       |                                      |                      |
|---------------------------------------|--------------------------------------|----------------------|
| 1. Service affecting trouble detected | Not SA ticket for device             | SA ticket for device |
| 2. Not SA ticket                      | Create new SA ticket and append note |                      |
| 3. SA ticket exist                    | Reopen SA ticket and append note     |                      |
| 4 Wait 60 seconds and forward to HNOC |                                      |                      |

## Event Descriptions
### HNOC forwarding outage queue
* [_attempt_ticket_creation](../services/service-outage-monitor/actions/outage_monitoring/_attempt_ticket_creation.md)

## Event Descriptions
### HNOC forwarding affecting queue
* [_attempt_ticket_creation](../services/service-affecting-monitor/actions/_attempt_forward_to_asr.md)