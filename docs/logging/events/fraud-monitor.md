---
hide:
  - navigation
  - toc
---

# Fraud Monitor Event Logging

# Description

The goal of the `fraud-monitor` service is to process unread Fraud e-mails and create / re-open Fraud tickets for them.

## Process Workflows
![](../../images/fraud-monitor.png){loading=lazy}

## List of Decisions made by the Fraud Monitor service

### Workflow - Process e-mail
|     | Condition                                                             | Decision                                                                            | Decision                                                                                    |
|-----|-----------------------------------------------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| 1   | Check for the e-mail subject to see if it is related to a Fraud alert | E-mail subject contains "Possible Fraud" or "Request Rate Monitor Violation (High)" | E-mail subject does NOT contain "Possible Fraud" or "Request Rate Monitor Violation (High)" |
| 2   | Check for the shape of the e-mail body                                | Format of the e-mail body is correct                                                | E-mail body is malformed                                                                    |
| 3   | Check if the e-mail was processed                                     | E-mail couldn't be processed                                                        | E-mail could be processed normally                                                          |

### Workflow - Process Fraud Alert
|     | Condition                                                           | Decision                 | Decision              |
|-----|---------------------------------------------------------------------|--------------------------|-----------------------|
| 1   | Check if client info could be found in Bruin for the service number | No client info was found | Client info was found |

### Workflow - Report Fraud to Bruin
|     | Condition                                                                     | Decision                    | Decision                        |
|-----|-------------------------------------------------------------------------------|-----------------------------|---------------------------------|
| 1   | Check if open Service Affecting tickets were found for the service number     | Open tickets were found     | No open tickets were found      |
| 2   | Check if resolved Service Affecting tickets were found for the service number | Resolved tickets were found | No resolved tickets were found  |
| 3   | Check if the ticket task related to the service number is already resolved    | Ticket task is NOT resolved | Ticket task is resolved already |

### Workflow - Append Fraud note to open ticket
|     | Condition                                                                                                  | Decision                                                          | Decision                                                                    |
|-----|------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------|
| 1   | Check if there's a Fraud note for the same Fraud appended to the ticket in the current documentation cycle | No note for the same Fraud has been appended in the ongoing cycle | A note for the same Fraud has been previously appended in the ongoing cycle |

### Workflow - Re-open ticket task
_No relevant business decisions are made in this workflow_

### Workflow - Create new Service Affecting ticket
|     | Condition                                                                                                 | Decision                                                                          | Decision                                                                              |
|-----|-----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| 1   | Check if there is Site and Ticket contacts to use on ticket creation for the client ID and service number | Site and Ticket contacts could be determined for the client ID and service number | Site and Ticket contacts could NOT be determined for the client ID and service number |

## Event Descriptions
### Schedule Fraud Monitoring job
* [start_fraud_monitoring](../services/fraud-monitor/actions/start_fraud_monitoring.md)

### Run Fraud Monitoring Process job
* [_fraud_monitoring_process](../services/fraud-monitor/actions/_fraud_monitoring_process.md)
