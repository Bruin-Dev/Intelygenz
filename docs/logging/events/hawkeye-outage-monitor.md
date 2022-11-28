---
hide:
  - navigation
  - toc
---

# Hawkeye Outage Monitor Event Logging

# Description
The Hawkeye Outage Monitor service is responsible for monitoring Ixia devices periodically. The monitoring process makes
sure to create or re-open Service Outage tickets if these devices stay offline for some time, and it also takes care of
auto-resolving any open tickets if the device comes back online.

## Process Workflows
![](../../images/hawkeye-outage-monitor.png){loading=lazy}

## List of Decisions made by the Hawkeye Outage Monitor service
### Overall workflow
|     | Condition                                                                          | Decision                                                 | Decision                                                  |
|-----|------------------------------------------------------------------------------------|----------------------------------------------------------|-----------------------------------------------------------|
| 1   | Check for the status of Ixia devices                                               | Node to Node AND Real Service status are both 1 (Online) | Node to Node OR Real Service status are 0 (Offline)       |
| 2   | Check for the status of Ixia devices after sitting in the quarantine for some time | Node to Node AND Real Service status are both 1 (Online) | Node to Node OR Real Service status are still 0 (Offline) |

### Workflow - Prepare data set for analysis
|     | Condition                                                                          | Decision                                                 | Decision                                                  |
|-----|------------------------------------------------------------------------------------|----------------------------------------------------------|-----------------------------------------------------------|
| 1   | Check for activity status of Ixia devices                                          | Any device is active                                     | None of the devices is currently active                   |

### Workflow - Auto-Resolution
|     | Condition                                                                                   | Decision                                                                  | Decision                                                                |
|-----|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------------------------|
| 1   | Check for existing open Service Outage ticket for the Ixia device                           | Open ticket found                                                         | No open tickets found                                                   |
| 2   | Check for creator of the open ticket                                                        | Ticket was created by the IPA system                                      | Ticket was NOT created by the IPA system                                |
| 3   | Check if the last outage was documented long time ago                                       | Less than 90 min have passed since the last outage was documented         | More than 90 min have passed since the last outage was documented       |
| 4   | Check if the number of auto-resolves allowed for the ticket task has been maxed out already | Ticket task linked to the device has been auto-resolved less than 3 times | Ticket task linked to the device has been auto-resolved 3 times or more |
| 5   | Check if the ticket task linked to the Ixia device is already resolved                      | Ticket task linked to the device is NOT resolved                          | Ticket task linked to the device is already resolved                    |

### Workflow - Ticket Creation / Task Re-Open
|     | Condition                                                                               | Decision                                                        | Decision                                                               | Decision                                                                                                         | Decision                                                                                                     | Decision                                                                                                                            |
|-----|-----------------------------------------------------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| 1   | Check the status returned by Bruin after trying to create a ticket for the Ixia device  | Ticket was created (Bruin status 200)                           | Ticket with open task already exists for the device (Bruin status 409) | Ticket with Resolved task exists for the device, but Bruin could not re-open it automatically (Bruin status 471) | Ticket with Resolved task exists for the device, and was automatically re-opened by Bruin (Bruin status 472) | Resolved ticket exists for the device and site (physical location) - a new task was automatically added by Bruin (Bruin status 473) |
| 2   | Check if there's a Triage note appended for a task belonging to an existing open ticket | Ticket task linked to the device has NOT a Triage note appended | Ticket task linked to the device already has a Triage note appended    |                                                                                                                  |                                                                                                              |                                                                                                                                     |

## Event Descriptions
### Schedule Hawkeye Outage Monitoring job
* [start_hawkeye_outage_monitoring](../services/hawkeye-outage-monitor/actions/outage_monitoring/start_hawkeye_outage_monitoring.md)

### Run Hawkeye Outage Monitoring job
* [_outage_monitoring_process](../services/hawkeye-outage-monitor/actions/outage_monitoring/_outage_monitoring_process.md)