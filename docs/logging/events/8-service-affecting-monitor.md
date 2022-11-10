# Service Affecting Monitor Event Logging

# Description
The Service Affecting Monitor service has three responsibilities:

* Monitor VeloCloud edges periodically. The monitoring process makes sure to create tickets or re-open Service Affecting tasks
  if these edges are experiencing issues that impact the quality of their service, and it also takes care of auto-resolving
  any open ticket tasks if the edge stabilizes.

    Monitored Service Affecting troubles are:

    * Latency
    * Packet Loss
    * Jitter
    * Bandwidth Over-Utilization
    * Circuit Instability

* Deliver Reoccurring Trouble Reports weekly. These reports include a relation of edges' links and the tickets where at 
  least one of the Service Affecting troubles has been reported at least a few times in a specific period of time.

* Deliver Daily Bandwidth Reports. These reports include a relation of edges' links that have experienced Bandwidth Over-Utilization
  troubles, and the tickets where those troubles were documented.

## Process Workflows
![[](../../images/8-service-affecting-monitor.png)](../../images/8-service-affecting-monitor.png)

## List of Decisions made by the Service Affecting Monitor
### Bridge-like capabilities
#### Subject: task_dispatcher.service-affecting-monitor.ticket_forwards.success
_No relevant business decisions are made in this workflow_

### Use cases
#### Monitoring
##### Workflow - Check links for Latency issues
|     | Condition                                      | Decision                                     | Decision                                         |
|-----|------------------------------------------------|----------------------------------------------|--------------------------------------------------|
| 1   | Check if Latency metrics are within thresholds | Link's metrics are within Latency thresholds | Link's metrics are NOT within Latency thresholds |

##### Workflow - Check links for Packet Loss issues
|     | Condition                                          | Decision                                         | Decision                                             |
|-----|----------------------------------------------------|--------------------------------------------------|------------------------------------------------------|
| 1   | Check if Packet Loss metrics are within thresholds | Link's metrics are within Packet Loss thresholds | Link's metrics are NOT within Packet Loss thresholds |

##### Workflow - Check links for Jitter issues
|     | Condition                                     | Decision                                    | Decision                                        |
|-----|-----------------------------------------------|---------------------------------------------|-------------------------------------------------|
| 1   | Check if Jitter metrics are within thresholds | Link's metrics are within Jitter thresholds | Link's metrics are NOT within Jitter thresholds |

##### Workflow - Check links for Bandwidth Over-Utilization issues
|     | Condition                                                         | Decision                                                        | Decision                                                            |
|-----|-------------------------------------------------------------------|-----------------------------------------------------------------|---------------------------------------------------------------------|
| 1   | Check if Bandwidth Over-Utilization metrics are within thresholds | Link's metrics are within Bandwidth Over-Utilization thresholds | Link's metrics are NOT within Bandwidth Over-Utilization thresholds |

##### Workflow - Check links for Circuit Instability issues
|     | Condition                                                  | Decision                                                 | Decision                                                     |
|-----|------------------------------------------------------------|----------------------------------------------------------|--------------------------------------------------------------|
| 1   | Check if Circuit Instability metrics are within thresholds | Link's metrics are within Circuit Instability thresholds | Link's metrics are NOT within Circuit Instability thresholds |

##### Workflow - Filter out links whose edges shouldn't be monitored
|     | Condition                                 | Decision                       | Decision                             |
|-----|-------------------------------------------|--------------------------------|--------------------------------------|
| 1   | Check for validity of link's edge state   | Link's edge state is invalid   | Link's edge state is valid           |
| 2   | Check for activation state of link's edge | Link's edge has been activated | Link's edge has never been activated |

##### Workflow - Report trouble to Bruin
|     | Condition                                                                  | Decision                    | Decision                        |
|-----|----------------------------------------------------------------------------|-----------------------------|---------------------------------|
| 1   | Check if open Service Affecting tickets were found for the link's edge     | Open tickets were found     | No open tickets were found      |
| 2   | Check if resolved Service Affecting tickets were found for the link's edge | Resolved tickets were found | No resolved tickets were found  |
| 3   | Check if the ticket task related to the link's edge is already resolved    | Ticket task is NOT resolved | Ticket task is resolved already |

##### Workflow - Append trouble note to open ticket
|     | Condition                                                                                                      | Decision                                                            | Decision                                                                      |
|-----|----------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------------------|
| 1   | Check if there's a trouble note for the same trouble appended to the ticket in the current documentation cycle | No note for the same trouble has been appended in the ongoing cycle | A note for the same trouble has been previously appended in the ongoing cycle |
| 2   | Check if link is BYOB or Customer Provided                                                                     | Link is BYOB or Customer Provided                                   | Link is NOT BYOB or Customer Provided                                         |
| 3   | Check when the last reminder e-mail was sent for the BYOB / Customer Provided link                             | Last reminder e-mail was sent to the customer more than 24h ago     | Last reminder e-mail was sent to the customer less than 24h ago               |

##### Workflow - Re-open ticket task
|     | Condition                                  | Decision                                                | Decision                                             |
|-----|--------------------------------------------|---------------------------------------------------------|------------------------------------------------------|
| 1   | Check if link is BYOB or Customer Provided | Link is BYOB or Customer Provided                       | Link is NOT BYOB or Customer Provided                |
| 2   | Check for time at impacted site            | Time at impacted site is between 12 am and 8 am (NIGHT) | Time at impacted site is between 8am and 12am. (DAY) |

##### Workflow - Create new Service Affecting ticket
|     | Condition                                                      | Decision                                                | Decision                                              |
|-----|----------------------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------|
| 1   | Check if link is currently under a Circuit Instability trouble | Link is under a Circuit Instability issue               | Link is under an issue other than Circuit Instability |
| 2   | Check if link is BYOB or Customer Provided                     | Link is BYOB or Customer Provided                       | Link is NOT BYOB or Customer Provided                 |
| 3   | Check for time at impacted site                                | Time at impacted site is between 12 am and 8 am (NIGHT) | Time at impacted site is between 8am and 12am. (DAY)  |

##### Workflow - Forward ticket task to ASR Investigate
|     | Condition                                                                               | Decision                                                                       | Decision                                                                              |
|-----|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| 1   | Check if link type is Wired                                                             | Link type is Wired                                                             | Link type is NOT Wired                                                                |
| 2   | Check if link is any of BYOB, Customer Owned, or PIAB, or its label is an IP address    | Link is NOT BYOB, Customer Owned or a PIAB, and its label is NOT an IP address | Link is BYOB, Customer Owned or a PIAB, or its label is an IP address                 |
| 3   | Check if troubles other than Circuit Instability have been reported for the ticket task | Only Circuit Instability troubles have been reported for this ticket task      | Other troubles aside from Circuit Instability have been reported for this ticket task |
| 4   | Check if ticket task has been forwarded to ASR before                                   | Ticket task has never been forwarded to ASR before                             | Ticket task has been forwarded to ASR previously                                      |

##### Workflow - Run Auto-Resolve for all stable links
|     | Condition                    | Decision                                                 | Decision                                            |
|-----|------------------------------|----------------------------------------------------------|-----------------------------------------------------|
| 1   | Check if link has stabilized | The link is under at least one Service Affecting trouble | The link is NOT under any Service Affecting trouble |

##### Workflow - Run Auto-Resolve for one single ticket
|     | Condition                                                                                  | Decision                                                           | Decision                                                         |
|-----|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------|------------------------------------------------------------------|
| 1   | Check for creator of the open ticket                                                       | Ticket was created by the IPA system                               | Ticket was NOT created by the IPA system                         |
| 2   | Check if link is BYOB and the ticket task is currently sitting in the IPA queue            | Link is BYOB and ticket task is currently sitting in the IPA queue | Link is NOT BYOB and ticket task is NOT sitting in the IPA queue |
| 3   | Check for time at impacted site                                                            | Time at impacted site is between 12 am and 8 am (NIGHT)            | Time at impacted site is between 8am and 12am. (DAY)             |
| 4   | Check if time elapsed since last trouble was documented is more or less than 3 hrs (NIGHT) | Last trouble was documented less than 3h ago                       | Last trouble was documented more than 3h ago                     |
| 5   | Check if time elapsed since last trouble was documented is more or less than 90 min (DAY)  | Last trouble was documented less than 90 min ago                   | Last trouble was documented more than 90 min ago                 |
| 6   | Check if max auto-resolves threshold has been exceeded for the ticket task                 | Ticket task has been auto-resolved less than 3 times               | Ticket task has been auto-resolved 3 times or more               |
| 7   | Check if ticket task is resolved already                                                   | Ticket task is resolved already                                    | Ticket task is NOT resolved                                      |

#### Reoccurring Trouble Reports
|     | Condition                                                            | Decision                                                                           | Decision                                                                          |
|-----|----------------------------------------------------------------------|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 1   | Check if data matching the criteria was found to populate the report | No links have been under the same trouble type 3 times or more in the last 14 days | Any link has been under the same trouble type 3 times or more in the last 14 days |

#### Daily Bandwidth Report
|     | Condition                                                            | Decision                                                    | Decision                                                 |
|-----|----------------------------------------------------------------------|-------------------------------------------------------------|----------------------------------------------------------|
| 1   | Check if data matching the criteria was found to populate the report | No tickets with Bandwidth Over-Utilization notes were found | Tickets with Bandwidth Over-Utilization notes were found |


## Event Descriptions
### Bridge-like capabilities
#### Subject: task_dispatcher.service-affecting-monitor.ticket_forwards.success
* [handle_ticket_forward](../services/service-affecting-monitor/actions/handle_ticket_forward/success.md)

### Use cases
#### Monitoring
##### Schedule Service Affecting Monitoring job
* [start_service_affecting_monitor](../services/service-affecting-monitor/actions/service_affecting_monitor/start_service_affecting_monitor.md)

##### Run Service Affecting Monitoring job
* [_service_affecting_monitor_process](../services/service-affecting-monitor/actions/service_affecting_monitor/_service_affecting_monitor_process.md)

#### Reoccurring Trouble Reports
##### Schedule Reoccurring Trouble Reports job
* [start_service_affecting_monitor_reports_job](../services/service-affecting-monitor/actions/service_affecting_monitor_reports/start_service_affecting_monitor_reports_job.md)

##### Run Reoccurring Trouble Reports job
* [monitor_reports](../services/service-affecting-monitor/actions/service_affecting_monitor_reports/monitor_reports.md)

#### Daily Bandwidth Report
##### Schedule Daily Bandwidth Report job
* [start_bandwidth_reports_job](../services/service-affecting-monitor/actions/bandwidth_reports/start_bandwidth_reports_job.md)

##### Run Daily Bandwidth Report job
* [_bandwidth_reports_job](../services/service-affecting-monitor/actions/bandwidth_reports/_bandwidth_reports_job.md)