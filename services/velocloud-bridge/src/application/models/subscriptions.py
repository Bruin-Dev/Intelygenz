from dataclasses import dataclass
from framework.nats.models import Subscription


@dataclass(kw_only=True)
class GetLinksWithEdgeInfo(Subscription):
    subject: str = "get.links.with.edge.info"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class EventEdgesForAlert(Subscription):
    subject: str = "alert.request.event.edge"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class EnterpriseEdgeList(Subscription):
    subject: str = "request.enterprises.edges"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class EventEnterpriseForAlert(Subscription):
    subject: str = "alert.request.event.enterprise"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class EnterpriseNameList(Subscription):
    subject: str = "request.enterprises.names"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class GetEdgeLinksSeries(Subscription):
    subject: str = "request.edge.links.series"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class LinksConfiguration(Subscription):
    subject: str = "request.links.configuration"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class LinksMetricInfo(Subscription):
    subject: str = "get.links.metric.info"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class NetworkEnterpriseEdgeList(Subscription):
    subject: str = "request.network.enterprise.edges"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class NetworkGatewayList(Subscription):
    subject: str = "request.network.gateway.list"
    queue: str = "velocloud_bridge"


@dataclass(kw_only=True)
class GatewayStatusMetrics(Subscription):
    subject: str = "request.gateway.status.metrics"
    queue: str = "velocloud_bridge"
