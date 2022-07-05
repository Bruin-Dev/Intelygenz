# IPA Event Logging

## Process Workflows 
![](../../images/4-SA-forward-to-ASR.jpg)

## List of Decisions made by the IPA System
### Service Affecting 
#### Circuit Instability
|||||
|---------------------|----------------------|-------------------------|-------------------------|
| **1. Check for existing SA ticket for SD-WAN**| SA ticket does not exist for SD-WAN | Resolved SA ticket exists for SD-WAN | Open/In progress SA ticket exist for SD-WAN |

||||
|---------------------|----------------------|-------------------------|
| **2. Check for other troubles on the ticket** | Other trouble is documented on ticket. (Jitter, Latency, Packet Loss, Bandwidth) | Only Circuit Instability is the only documented trouble on the ticket |
| **3. Checking what kind of link the instability was detected on** | Instability was detected for Wireless Link | Instability was detected for Wired Link|
| **4. Checking wired link's name for BYOB or Customer Owned**| Wired Link name contains BYOB or Customer Owned | Wired Link name does NOT contain BYOB or Customer Owned |
| **5. Checking if the wired link name is an IP** | Wired link name is an IP | Wired link name is NOT an IP |


## Event Descriptions
### Service Affecting 
* [Bouncing check](../services/service-affecting-monitor/actions/_bouncing_check.md)
