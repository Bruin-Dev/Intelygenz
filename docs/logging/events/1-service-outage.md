# IPA Event Logging

## Process Workflows 
![](../../images/1-service-outage.jpg)

## List of Decisions made by the IPA System
### Service Outage
####  Start of Service Outage process

||||
|---------------------|----------------------|-------------------------|
|**1. Checking edge & link status for outage** |   Outage is detected | Outage is not detected  |

####  Autoresolution

||||
|---------------------|-------------------------|---------------------|
|**2. Checking for non-resolved task for Service Outage ticket**| A non-resolved task exists for the SD-WAN on a Service Outage ticket | No non-resolved task exists for the SD-WAN|
|**3. Checking for time at impacted site**| Time at impacted site is between 12am and 6am (NIGHT) | Time at impacted site is between 6am and 12am (DAY) |
|**4. Checking if time passed is more or less than 3 hrs**| More than 3 hours has passed since an outage was documented | Less than 3 hours has passed since an outage was documented |
|**5. Checking if time passed is more or less than 90 mins**| More than 90 mins has passed since an outage was documented | Less than 90 mins has passed since an outage was documented | 
|**6. Checking how mamy time ticket has been autoresolved**| Ticket has been autoresolved less than 3 times | Ticket has been autoresolved more than 3 times |

#### Ticket Creation

||||
|---------------------|-------------------------|-------------------------|
|**7. Checking the results of ticket creation attempt**| New ticket is created with a task for the SD-WAN and placed in an IPA queue   | Ticket already exists for the location|

|||||
|-------------------------|-------------------------|-------------------------|-------------------------|
|**8. Determining what to do with an already existing ticket**|New task for SD-WAN is added to ticket | SD-WAN task on existing ticket for is reopened  | In-progress tasks for SD-WAN already exists |    

#### IPA queue

||||
|---------------------|-------------------------|-------------------------|
| **9. What type of Outage was caused**| Outage Detected is an EDGE DOWN| Outage Detected is a LINK DOWN|
|**10. Checking time at impacted site**|Time at impacted site is between 12am and 6am (NIGHT)|Time at impacted site is between 6am and 12am (DAY)|

#### DiGi Reboot 

||||
|---------------------|-------------------------|-------------------------|
|**11. Are there any DiGi links**| Edge has at least one offline DiGi link| Edge has no offline DiGi links|
|**12. Has a DiGi reboot been attempted**|DiGi reboot has not been attempted yet|DiGi reboot has been attempted|
|**13. Has the DiGi reboot attempt occur after 30 mins** |30 min has passed since reboot started|30 min has not passed since reboot started|


## Event Descriptions
### Service Outage
* [start_service_outage_monitoring](../services/service-outage-monitor/actions/outage_monitoring/start_service_outage_monitoring.md)

 
 



 

 








