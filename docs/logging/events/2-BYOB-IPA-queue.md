# IPA Event Logging

## Process Workflows 
![](../../images/2-BYOB-IPA-queue.jpg)

## List of Decisions made by the IPA System
### BYOB IPA queue
#### Start of BYOB workflow

||||
|---------------------|----------------------|----------------------|
| **1. Determining whether or not there is an ongoing trouble or not** | Trouble is detected | Trouble stabilized |


#### Trouble is detected

||||
|---------------------|----------------------|----------------------|
| **2. Determining what kind of trouble occurred** | Trouble is on the link | Trouble is on the Edge |
| **3. Determining what VCO does the troubled device belong too** | VCO 1, 2, 3| VCO 4 |
| **4. Determining if link name includes "BYOB" or "Customer Provided"**| Link name includes "BYOB" or "Customer Provided" | Link name doesn't include "BYOB" or "Customer Provided" |

#### Trouble stabilized

||||
|---------------------|----------------------|----------------------|
| **5. Determining what kind of trouble last occurred** | Trouble is on the link | Trouble is on the Edge |
| **6. Determining what VCO does the device belong too** | VCO 1, 2, 3| VCO 4 |
| **7. Determining if link name includes "BYOB" or "Customer Provided"**| Link name includes "BYOB" or "Customer Provided" | Link name doesn't include "BYOB" or "Customer Provided" |

## Event Descriptions 
### BYOB IPA queue
* [_attempt_ticket_creation](../services/service-outage-monitor/actions/outage_monitoring/_attempt_ticket_creation.md)