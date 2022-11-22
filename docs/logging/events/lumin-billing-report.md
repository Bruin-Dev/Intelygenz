---
hide:
  - navigation
  - toc
---

# Last Contact Report Event Logging

# Description

The Lumin Billing Report service is responsible for running a job every first day of the month. The job makes sure to
gather all the billable events registered during the past month in the LuminAI system, and send a summary of those events
via e-mail.

## Process Workflows
![[](../../images/lumin-billing-report.png)](../../images/lumin-billing-report.png)

## List of Decisions made by the Lumin Billing Report service
_This service does not make any business decision_

## Event Descriptions
### Schedule Lumin Billing Report job
* [start_billing_report_job](../services/lumin-billing-report/actions/billing_report/start_billing_report_job.md)

### Run Lumin Billing Report job
* [_billing_report_process](../services/lumin-billing-report/actions/billing_report/_billing_report_process.md)
