# Intermapper Event Logging

## Process Workflows
![[](../../images/9-intermapper-monitor.png)](../../images/9-intermapper-monitor.png)

## List of Decisions made by the Intermapper System
### Intermapper queue
#### Start of intermapper workflow
|                                                                               |                                                          |                                         |
|-------------------------------------------------------------------------------|----------------------------------------------------------|-----------------------------------------|
| 1. Check sender email                                                         | Sender email is noreply@mettel.net                       | Sender email is NOT noreply@mettel.net  |
| 2. Check for Alpha-numeric-value (Circuit id) from subject within parenthesis | Alpha-numeric value (Circuit ID) can be parsed from subject between parenthsis to identify inventory |  Alpha-numeric value (Circuit ID) can NOT be parsed from email subject between parenthsis |
| 3. Check for Warning event type and condition                                 | Event type is NOT Warning and Condition is NOT "WAN Interface down - Device is running on LTE Interface" | Event type is Warning and Condition is "WAN Interface down - Device is running on LTE Interface" |
| 4. Check for event type                                                       | Event type is Alarm, Critical, Warning, or Down | Event type is Up, OK |
| 5. Check probe type                                                           | Probe type is Data Remote | Probe Type is NOT Data Remote |
| 6. Check to see if we can retrieve data from DRI                              | Successfully retrieved data from DRI from Inventory | Could not retrieve any data for inventory from DRI |
| 7. Checking for non-resolved task for Service Outage ticket                   | A non-resolved task exists for the inventory on a Service Outage ticket | No non-resolved task exists for the inventory on a Service Outage ticket |
| 8. Checking for time at impacted site                                         | Time at impacted site is between 12am and 6am (NIGHT) | Time at impacted site is between 6am and 12am (DAY) |
| 9. Checking if time passed is more or less than 3 hrs                         | More than 3 hours has passed since an outage was documented | Less than 3 hours has passed since an outage was documented |
| 10. Checking if time passed is more or less than 90 mins                      | More than 90 mins has passed since an outage was documented | Less than 90 mins has passed since an outage was documented | 
| 11. Checking how mamy time ticket has been autoresolved                       | Ticket has been autoresolved less than 3 times | Ticket has been autoresolved more than 3 times |                                                                           
## Event Descriptions
### Intermapper queue
* [start_intermapper_outage_monitoring](../services/intermapper-outage-monitor/actions/start_intermapper_outage_monitoring.md)