# VeloCloud Bridge Event Logging

# Description

The mission of this service is to act as a proxy to the VeloCloud API. It accepts requests from other services and yields
the requested data back to those services, so they can make the appropriate business decision.

## Process Workflows
![[](../../images/12-velocloud-bridge.png)](../../images/12-velocloud-bridge.png)

## List of Decisions made by the VeloCloud Bridge
### Subject: alert.request.event.edge (aims at endpoint [POST /event/getEnterpriseEvents](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/event/event_get_enterprise_events))
|     | Condition                                                         | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                   | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /event/getEnterpriseEvents | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: request.enterprises.edges (aims at endpoint [POST /enterprise/getEnterpriseEdges](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/enterprise/enterprise_get_enterprise_edges))
|     | Condition                                                             | Decision                     | Decision                         |
|-----|-----------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                       | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /enterprise/getEnterpriseEdges | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: alert.request.event.enterprise (aims at endpoint [POST /event/getEnterpriseEvents](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/event/event_get_enterprise_events))
|     | Condition                                                         | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                   | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /event/getEnterpriseEvents | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: request.enterprises.names (aims at endpoint [POST /monitoring/getAggregates](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/monitoring/monitoring_get_aggregates))
|     | Condition                                                        | Decision                     | Decision                         |
|-----|------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                  | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /monitoring/getAggregates | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: request.edge.links.series (aims at endpoint [POST /metrics/getEdgeLinkSeries](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/metrics/metrics_get_edge_link_series))
|     | Condition                                                         | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                   | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /metrics/getEdgeLinkSeries | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: request.links.configuration (aims at endpoint [POST /edge/getEdgeConfigurationModules](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/edge/edge_get_edge_configuration_modules))
|     | Condition                                                                | Decision                                  | Decision                                      |
|-----|--------------------------------------------------------------------------|-------------------------------------------|-----------------------------------------------|
| 1   | Check for shape and content of incoming request                          | Request has valid format                  | Request has invalid format                    |
| 2   | Check for status of response from POST /edge/getEdgeConfigurationModules | HTTP response has status 200              | HTTP response has NOT status 200              |
| 3   | Check for existence of WAN module in response                            | WAN configuration exists                  | WAN configuration does NOT exist              |
| 4   | Check for existence of links configurations in WAN module                | Links config defined in WAN configuration | Links config NOT defined in WAN configuration |

### Subject: get.links.metric.info (aims at endpoint [POST /monitoring/getAggregateEdgeLinkMetrics](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/monitoring/monitoring_get_aggregate_edge_link_metrics))
|     | Condition                                                                      | Decision                     | Decision                         |
|-----|--------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /monitoring/getAggregateEdgeLinkMetrics | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: get.links.with.edge.info (aims at endpoint [POST /monitoring/getEnterpriseEdgeLinkStatus](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/monitoring/monitoring_get_enterprise_edge_link_status))
|     | Condition                                                                      | Decision                     | Decision                         |
|-----|--------------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                                | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /monitoring/getEnterpriseEdgeLinkStatus | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: request.network.enterprise.edges (aims at endpoint [POST /network/getNetworkEnterprises](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/network/network_get_network_enterprises))
|     | Condition                                                             | Decision                     | Decision                         |
|-----|-----------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                       | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /network/getNetworkEnterprises | HTTP response has status 200 | HTTP response has NOT status 200 |
| 3   | Check enterprise was found for specified filters                      | Enterprise found for filters | Enterprise NOT found for filters |
| 4   | Check enterprise has edges                                            | Edges found for enterprises  | Edges NOT found for enterprises  |

### Subject: request.network.gateway.list (aims at endpoint [POST /network/getNetworkGateways](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/network/network_get_network_gateways))
|     | Condition                                                          | Decision                     | Decision                         |
|-----|--------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                    | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /network/getNetworkGateways | HTTP response has status 200 | HTTP response has NOT status 200 |

### Subject: request.gateway.status.metrics (aims at endpoint [POST /metrics/getGatewayStatusMetrics](https://vdc-download.vmware.com/vmwb-repository/dcr-public/5b27c4a1-c44d-4806-b2d8-f03ab51f3109/c8bb0795-f567-4781-9176-a442c64a2f74/index-4.4.0-dist.html#/metrics/metrics_get_gateway_status_metrics))
|     | Condition                                                               | Decision                     | Decision                         |
|-----|-------------------------------------------------------------------------|------------------------------|----------------------------------|
| 1   | Check for shape and content of incoming request                         | Request has valid format     | Request has invalid format       |
| 2   | Check for status of response from POST /metrics/getGatewayStatusMetrics | HTTP response has status 200 | HTTP response has NOT status 200 |

## Event Descriptions
### Subject: alert.request.event.edge
* [edge_events_for_alert](../services/velocloud-bridge/actions/edge_events_for_alert.md)

### Subject: request.enterprises.edges
* [enterprise_edge_list](../services/velocloud-bridge/actions/enterprise_edge_list.md)

### Subject: alert.request.event.enterprise
* [enterprise_events_for_alert](../services/velocloud-bridge/actions/enterprise_events_for_alert.md)

### Subject: request.enterprises.names
* [enterprise_name_list_response](../services/velocloud-bridge/actions/enterprise_name_list_response.md)

### Subject: request.edge.links.series
* [get_edge_links_series](../services/velocloud-bridge/actions/get_edge_links_series.md)

### Subject: request.links.configuration
* [links_configuration](../services/velocloud-bridge/actions/links_configuration.md)

### Subject: get.links.metric.info
* [links_metric_info](../services/velocloud-bridge/actions/links_metric_info.md)

### Subject: get.links.with.edge.info
* [links_with_edge_info](../services/velocloud-bridge/actions/links_with_edge_info.md)

### Subject: request.network.enterprise.edges
* [network_enterprise_edge_list](../services/velocloud-bridge/actions/network_enterprise_edge_list.md)

### Subject: request.network.gateway.list
* [network_gateway_list](../services/velocloud-bridge/actions/network_gateway_list.md)

### Subject: request.gateway.status.metrics
* [gateway_status_metrics](../services/velocloud-bridge/actions/gateway_status_metrics.md)
