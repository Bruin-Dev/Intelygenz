# DiGi Reboot Report Event Logging

# Description

The `digi-reboot-report` service creates a daily report based on the DiGi recovery logs from the last 3 days, 
and then emails it out.

## Process Workflows
![[](../../images/digi-reboot-report.png)](../../images/digi-reboot-report.png)

## List of Decisions made by the Digi Reboot Report service
_This service does not make any business decision_

## Event Descriptions
### Schedule Lumin Billing Report job
* [start_digi_reboot_report_job](../services/digi-reboot-report/actions/start_digi_reboot_report_job.md)

### Run Digi Reboot Report job
* [_digi_reboot_report_process](../services/digi-reboot-report/actions/_digi_reboot_report_process.md)