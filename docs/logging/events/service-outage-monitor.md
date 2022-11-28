---
hide:
  - navigation
  - toc
---

# Service Outage Monitor Event Logging

# Description
The Service Outage Monitor service has two responsibilities:

* Monitor VeloCloud edges periodically. The monitoring process makes sure to create tickets or re-open Service Outage tasks
  if these edges or any of their links are down, and it also takes care of auto-resolving any open ticket tasks if the edge comes
  back online.

    Monitored outages are:

    * Link Down - HA disabled
    * Hard Down - HA disabled
    * Link Down - HA enabled
    * Soft Down - HA enabled
    * Hard Down - HA enabled

* Append Triage and Events notes to tickets. Under certain conditions, the IPA system fails to append Triage notes right after
  creating a ticket or re-opening an existing task. This last resort mechanism ensures that those tickets get a Triage note
  appended at some point.

    At the same time, this process makes sure to update tickets already having Triage notes with notes gathering the details
    of the latest events found in VeloCloud for a particular edge. These are known as Events notes.

## Process Workflows
![](../../images/service-outage-monitor.png){loading=lazy}

## List of Decisions made by the Service Outage Monitor
### Bridge-like capabilities
#### Subject: task_dispatcher.service-outage-monitor.ticket_forwards.success
_No relevant business decisions are made in this workflow_

### Use cases
#### Monitoring
##### Overall workflow
|     | Condition                                                                                                                                           | Decision                                                                        | Decision                                                                                       |
|-----|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1   | Check for the status of VeloCloud edges                                                                                                             | Edge state is ONLINE, and all its links are STABLE                              | Edge state is OFFLINE, or any of its links is DISCONNECTED                                     |
| 2   | Check if the outage detected for an edge should be documented to a ticket attending to its HA condition (primary or standby) and the type of outage | Detected outage should be documented in a ticket                                | Detected outage should NOT be documented in a ticket                                           |
| 3   | Check for the grade of VeloCloud edges' links (Business vs. Commercial)                                                                             | Any of the edge's links is DISCONNECTED plus that link is a Business Grade link | Edge is OFFLINE, or any of its links is DISCONNECTED plus that link is a Commercial Grade link |
| 4   | Check for the status of VeloCloud edges after sitting in the quarantine for some time                                                               | Edge state is ONLINE, and all its links are STABLE                              | Edge is still OFFLINE, or any of its links is still DISCONNECTED                               |

##### Workflow - Ticket Creation / Task Re-Open
|     | Condition                                                                                 | Decision                                                        | Decision                                                             | Decision                                                                                                      | Decision                                                                                                   | Decision                                                                                                                          |
|-----|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| 1   | Check the status returned by Bruin after trying to create a ticket for the VeloCloud edge | Ticket was created (Bruin status 200)                           | Ticket with open task already exists for the edge (Bruin status 409) | Ticket with Resolved task exists for the edge, but Bruin couldn't re-open it automatically (Bruin status 471) | Ticket with Resolved task exists for the edge, and was automatically re-opened by Bruin (Bruin status 472) | Resolved ticket exists for the edge and site (physical location) - a new task was automatically added by Bruin (Bruin status 473) |

##### Workflow - Filter out edges that shouldn't be monitored
|     | Condition                          | Decision                | Decision                      |
|-----|------------------------------------|-------------------------|-------------------------------|
| 1   | Check for validity of edge state   | Edge state is invalid   | Edge state is valid           |
| 2   | Check for activation state of edge | Edge has been activated | Edge has never been activated |

##### Workflow - Append Triage note to ticket task for edge
_No relevant business decisions are made in this workflow_

##### Workflow - Change ticket severity
|     | Condition                                           | Decision                                                                   | Decision                                                             |
|-----|-----------------------------------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------|
| 1   | Check type of outage for edge                       | Edge is OFFLINE                                                            | Edge is ONLINE, and any of its links is DISCONNECTED                 |
| 2   | Check current ticket severity for Edge Down outages | Ticket severity is NOT set to 2 (Medium/High) already                      | Ticket severity is already set to 2 (Medium/High)                    |
| 3   | Check status returned by Bruin on ticket creation   | Bruin returned a 409, 471, or 472 status while trying to create the ticket | Bruin returned a 200 or 473 status while trying to create the ticket |
| 4   | Check for ticket having multiple open tasks         | Ticket has multiple open tasks                                             | Only the ticket task for the edge is open                            |
| 5   | Check current ticket severity for Link Down outages | Ticket severity is NOT set to 3 (Low/Medium) already                       | Ticket severity is already set to 3 (Low/Medium)                     |

##### Workflow - Forward ticket task to HNOC
|     | Condition                                                                                     | Decision                                                        | Decision                                                                                                    | Decision                                                                                                |
|-----|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| 1   | Check type of outage for edge, and BYOB condition of links for Link Down outages              | Edge is OFFLINE                                                 | Edge is ONLINE, and any of its links is DISCONNECTED plus that link is NOT a BYOB or Customer Provided link | Edge is ONLINE, and any of its links is DISCONNECTED plus that link is a BYOB or Customer Provided link |
| 2   | Check for time at impacted site                                                               | Time at impacted site is between 12 am and 8 am (NIGHT)         | Time at impacted site is between 8am and 12am. (DAY)                                                        |                                                                                                         |
| 3   | Check status returned by Bruin on ticket creation                                             | Bruin returned a 409 status while trying to create the ticket   | Bruin returned a 200, 471, 472, or 473 status while trying to create the ticket                             |                                                                                                         |
| 4   | Check the last time an e-mail reminder was sent via Bruin for a Link Down outage in BYOB link | Last reminder e-mail was sent to the customer less than 24h ago | Last reminder e-mail was sent to the customer more than 24h ago                                             |                                                                                                         |

##### Workflow - Forward ticket task to ASR
|     | Condition                                                    | Decision                                                                    | Decision                                                                |
|-----|--------------------------------------------------------------|-----------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 1   | Check type of outage for edge                                | Edge is OFFLINE                                                             | Edge is ONLINE, and any of its links is DISCONNECTED                    |
| 2   | Check type of disconnected link(s)                           | Any of the DISCONNECTED links is Wired                                      | None of the DISCONNECTED links is Wired                                 |
| 3   | Check if any of the disconnected wired links is BYOB or PIAB | None of the DISCONNECTED Wired links are BYOB, Customer Provided, or a PIAB | All the DISCONNECTED Wired links are BYOB, Customer Provided, or a PIAB |
| 4   | Check if ticket task has been forwarded to ASR before        | Ticket task has NOT been forwarded to ASR before                            | Ticket task has been forwarded to ASR before                            |

##### Workflow - Start reboot for DiGi links
|     | Condition                             | Decision                                | Decision                               |
|-----|---------------------------------------|-----------------------------------------|----------------------------------------|
| 1   | Check DiGi condition for edge's links | Edge has no DiGi links                  | Edge has DiGi links                    |
| 2   | Check status of DiGi links            | None of the DiGi links are DISCONNECTED | At least one DiGi link is DISCONNECTED |

##### Workflow - Check for failed reboot for DiGi links
|     | Condition                                                                                                       | Decision                                                                              | Decision                                                                                    |
|-----|-----------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 1   | Check DiGi condition for edge's links                                                                           | Edge has no DiGi links                                                                | Edge has DiGi links                                                                         |
| 2   | Check status of DiGi links                                                                                      | None of the DiGi links are DISCONNECTED                                               | At least one DiGi link is DISCONNECTED                                                      |
| 3   | Check for existence of DiGi Reboot related notes in ticket                                                      | No DiGi Reboot notes were found (i.e. no reboots were attempted before)               | DiGi Reboot note was found (i.e. a reboot was attempted before)                             |
| 4   | Check for the moment the DiGi link was last rebooted                                                            | DiGi link was rebooted recently                                                       | DiGi link was rebooted long time ago                                                        |
| 5   | Check if the DiGi Reboot note found is related to the DiGi link                                                 | DiGi Reboot note found is NOT related to the link                                     | DiGi Reboot note found is related to the link                                               |
| 6   | Check if the ticket task related to the DiGi link's edge has already been forwarded to the Wireless team before | Ticket task has been forwarded to the Wireless Repair Intervention Needed team before | Ticket task has never been forwarded to the Wireless Repair Intervention Needed team before |

##### Workflow - Re-open ticket task for edge
_No relevant business decisions are made in this workflow_

##### Workflow - Auto-Resolution
|     | Condition                                                                                                                                                                             | Decision                                                                   | Decision                                                                       |
|-----|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| 1   | Check if edge is in the auto-resolution blacklist                                                                                                                                     | Edge is blacklisted from auto-resolves                                     | Edge is NOT blacklisted from auto-resolves                                     |
| 2   | Check if an open Service Outage ticket was found for the edge                                                                                                                         | No open ticket was found                                                   | Open ticket was found                                                          |
| 3   | Check for creator of the open ticket                                                                                                                                                  | Ticket was created by the IPA system                                       | Ticket was NOT created by the IPA system                                       |
| 4   | Check if the outage documented in the ticket is a Link Down, if the link that was down is BYOB, and also if the ticket task related to the edge is currently sitting in the IPA queue | Edge has BYOB links, and ticket task is currently sitting in the IPA queue | Edge does NOT have BYOB links, and ticket task is NOT sitting in the IPA queue |
| 5   | Check for time at impacted site                                                                                                                                                       | Time at impacted site is between 12 am and 8 am (NIGHT)                    | Time at impacted site is between 8am and 12am. (DAY)                           |
| 6   | Check if time elapsed since last outage was documented is more or less than 3 hrs (NIGHT)                                                                                             | Last outage was documented less than 3h ago                                | Last outage was documented more than 3h ago                                    |
| 7   | Check if time elapsed since last outage was documented is more or less than 90 min (DAY)                                                                                              | Last outage was documented less than 90 min ago                            | Last outage was documented more than 90 min ago                                |
| 8   | Check if max auto-resolves threshold has been exceeded for the ticket task                                                                                                            | Ticket task has been auto-resolved less than 3 times                       | Ticket task has been auto-resolved 3 times or more                             |
| 9   | Check if ticket task is resolved already                                                                                                                                              | Ticket task is resolved already                                            | Ticket task is NOT resolved                                                    |

#### Triage
##### Workflow - Append Triage or Events note to ticket task without Triage note
|     | Condition                                                                                                               | Decision                          | Decision                      |
|-----|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------|-------------------------------|
| 1   | Check current state of the edge for which the Service Outage ticket was created / the ticket task was re-opened earlier | Edge is no longer in outage state | Edge is still in outage state |

##### Workflow - Append Events note to ticket task with Triage note
|     | Condition                                                                                     | Decision                                                   | Decision                                                   |
|-----|-----------------------------------------------------------------------------------------------|------------------------------------------------------------|------------------------------------------------------------|
| 1   | Check for the moment the last Events note was appended to the ticket task related to the edge | Last Events note was appended to ticket task very recently | Last Events note was appended to ticket task long time ago |


## Event Descriptions
### Bridge-like capabilities
#### Subject: task_dispatcher.service-outage-monitor.ticket_forwards.success
* [handle_ticket_forward](../services/service-outage-monitor/actions/handle_ticket_forward/success.md)

### Use cases
#### Monitoring
##### Schedule Service Outage Monitoring job
* [start_service_outage_monitoring](../services/service-outage-monitor/actions/service_outage_monitor/start_service_outage_monitoring.md)

##### Run Service Outage Monitoring job
* [_outage_monitoring_process](../services/service-outage-monitor/actions/service_outage_monitor/_outage_monitoring_process.md)

#### Triage
##### Schedule Triage job
* [start_triage_job](../services/service-outage-monitor/actions/triage/start_triage_job.md)

##### Run Triage job
* [_run_tickets_polling](../services/service-outage-monitor/actions/triage/_run_tickets_polling.md)
