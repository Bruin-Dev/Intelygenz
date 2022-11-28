---
hide:
  - navigation
  - toc
---

# Customer Cache Event Logging

# Description

The Customer Cache service has two responsibilities:

* Run a periodic job that retrieves non-volatile data from VeloCloud and Bruin for all edges across VCOs, and then cross the
  data from both systems and store the resulting cache to a Redis instance. The cache will remain valid until the next successful
  execution of the job.
* Serve the cache built from execution of the previously mentioned job to other services in the system.

## Process Workflows
![](../../images/customer-cache.png){loading=lazy}

## List of Decisions made by the Customer Cache service
### Bridge-like capabilities
#### Subject: customer.cache.get
|     | Condition                                                           | Decision                          | Decision                                 |
|-----|---------------------------------------------------------------------|-----------------------------------|------------------------------------------|
| 1   | Check for shape and content of incoming request                     | Request has valid format          | Request has invalid format               |
| 2   | Check for existence of the cache in Redis                           | Cache exists for all VCOs         | Cache does NOT exist for any of the VCOs |
| 3   | Check for Last Contact filter in the request payload                | Last Contact filter was specified | Last Contact filter was NOT specified    |
| 4   | Check for emptiness of cache after filtering by Last Contact filter | Resulting cache is NOT empty      | Resulting cache is empty                 |

### Use case
#### Overall workflow
|     | Condition                                                                                  | Decision                                                | Decision                                                    |
|-----|--------------------------------------------------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------|
| 1   | Check for edges successfully retrieved from the VCOs                                       | Edges are fetched from VCOs successfully                | An error happens while fetching all edges                   |
| 1   | Check if the threshold to retry fetching edges from the VCOs after a failure was maxed out | Threshold to retry fetching edges from VCOs was reached | Threshold to retry fetching edges from VCOs was NOT reached |

### Workflow - Fetch edge data from VeloCloud
|     | Condition                                                     | Decision                                             | Decision                                         |
|-----|---------------------------------------------------------------|------------------------------------------------------|--------------------------------------------------|
| 1   | Check for validity of edge state                              | Edge state is invalid                                | Edge state is valid                              |
| 2   | Check for activation state of edge                            | Edge has been activated                              | Edge has never been activated                    |
| 3   | Check if the edge is blacklisted from IPA System's monitoring | Edge is NOT blacklisted from IPA system's monitoring | Edge is blacklisted from IPA system's monitoring |

### Workflow - Fetch edge data from Bruin
|     | Condition                                                                                           | Decision                                                                                             | Decision                                                                   |
|-----|-----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| 1   | Check for existence of client info in Bruin for the edge                                            | Client info was found in Bruin inventories                                                           | No client info was found in Bruin inventories                              |
| 2   | Check if the management status of the edge is monitorable                                           | Management status is monitorable                                                                     | Management status is NOT monitorable                                       |
| 3   | Check if the management status of the edge is set to Pending and is blacklisted for certain clients | Management status is NOT Pending, or it is Pending and the client is NOT blacklisted for such status | Management status is Pending and the client is blacklisted for such status |

### Workflow - Cross VeloCloud and Bruin data & store cache
|     | Condition                                                                  | Decision                     | Decision                 |
|-----|----------------------------------------------------------------------------|------------------------------|--------------------------|
| 1   | Check if cache originated after crossing VeloCloud and Bruin data is empty | Resulting cache is NOT empty | Resulting cache is empty |


## Event Descriptions
### Bridge-like capabilities
#### Subject: customer.cache.get
* [get_customers](../services/customer-cache/actions/get_customers/get_customers.md)

### Use case
#### Schedule Customer Cache Refresh job
* [schedule_cache_refresh](../services/customer-cache/actions/refresh_cache/schedule_cache_refresh.md)

#### Run Customer Cache Refresh job
* [_refresh_cache](../services/customer-cache/actions/refresh_cache/_refresh_cache.md)
