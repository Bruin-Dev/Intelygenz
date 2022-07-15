# Intermapper Event Logging

# Description

The mission of this service is to analyze InterMapper events sent by one or more InterMapper instances via e-mail, where each
event refers to a device. The outcome of the analysis will determine whether:
* A new Bruin ticket is created, if the device is down.
* An existing Bruin ticket is re-opened, if the device is down and the ticket is resolved.
* An existing Bruin ticket is auto-resolved, if the device is up and the ticket is open.

When any of these cases take place, the event information is added to the ticket as a note. In some cases, this note can
be enriched with information from the DRI system.

Whatever the outcome of the analysis is, the event is finally marked as processed.

## Process Workflows
![[](../../images/9-intermapper-monitor.png)](../../images/9-intermapper-monitor.png)

## List of Decisions made by the Intermapper Monitor
### Process E-mail Batch workflow
|     | Condition                                | Decision                 | Decision                |
|-----|------------------------------------------|--------------------------|-------------------------|
| 1   | Check for Circuit ID existence in e-mail | Circuit ID is defined    | Circuit ID is undefined |
| 2   | Check for Circuit ID being an SD-WAN     | Circuit ID is not SD-WAN | Circuit ID is SD-WAN    |

#### Process E-mail workflow
|     | Condition            | Decision                                                     | Decision               | Decision                |
|-----|----------------------|--------------------------------------------------------------|------------------------|-------------------------|
| 1   | Check for Event Type | Event type is Alarm, Critical, Warning, Down or Link Warning | Event type is Up or OK | Event Type is any other |

#### Ticket Creation workflow
|     | Condition                                     | Decision                                                                               | Decision                                                                                      |
|-----|-----------------------------------------------|----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| 1   | Check for Probe Type                          | Probe Type is Data Remote                                                              | Probe Type is NOT Data Remote                                                                 |
| 2   | Check to see if we can retrieve data from DRI | Successfully retrieved data from DRI for Inventory                                     | Could not retrieve any data for inventory from DRI                                            |
| 3   | Check Probe Type and Condition of event       | Probe Type is Data Remote Probe AND Condition is Device Lost Power - Battery is in use | Probe Type is NOT Data Remote Probe or Condition is NOT Device Lost Power - Battery is in use |

#### Auto-Resolution workflow
|     | Condition                                                     | Decision                                                         | Decision                                                         |
|-----|---------------------------------------------------------------|------------------------------------------------------------------|------------------------------------------------------------------|
| 1   | Check to see if ticket's product category is in the whitelist | Ticket's product category is whitelisted                         | Ticket's product category is NOT whitelisted                     |
| 2   | Check for time at impacted site                               | Time at impacted site is between 12am and 6am (NIGHT)            | Time at impacted site is between 6am and 12am (DAY)              |
| 3   | Check if time passed is more or less than 3 hrs (NIGHT)       | Less than 3 hrs have passed since an outage has been documented  | More than 3 hrs have passed since an outage has been documented  |
| 4   | Check if time passed is more or less than 90 min (DAY)        | Less than 90 min have passed since an outage has been documented | More than 90 min have passed since an outage has been documented |
| 5   | Check if max auto-resolves threshold has been exceeded        | Ticket has been auto-resolved less than 3 times                  | Ticket has been auto-resolved 3+ times already                   |
| 6   | Check if ticket is resolved                                   | Ticket is resolved already                                       | Ticket is not resolved                                           |

## Event Descriptions
### Start InterMapper Outage Monitoring
* [start_intermapper_outage_monitoring](../services/intermapper-outage-monitor/actions/start_intermapper_outage_monitoring.md)

### Process E-mail Batch
* [_process_email_batch](../services/intermapper-outage-monitor/actions/_process_email_batch.md)

### Process E-mail
* [_process_email](../services/intermapper-outage-monitor/actions/_process_email.md)

### Ticket Creation
* [_create_outage_ticket](../services/intermapper-outage-monitor/actions/_create_outage_ticket.md)

### Auto-Resolution
* [_autoresolve_ticket](../services/intermapper-outage-monitor/actions/_autoresolve_ticket.md)