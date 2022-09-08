import logging

from application.data.velocloud.network_gateway import NetworkGateway
from application.handler import WillReturnJSON
from application.scenario import Scenario
from application.scenarios import timeout
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class ReportIncident(Scenario):
    name: str = "Report velocloud incident"

    async def run(self):
        # given ...
        # - Velocloud reports one offline gateway
        offline_gateway = NetworkGateway(gatewayState="OFFLINE")
        self.given("/portal/rest/network/getNetworkGateways", WillReturnJSON([offline_gateway.dict()]))

        # when
        # RTA polls for closed tickets

        # then

        return await self.check(
            # [servicenow-bridge] reports an incident
            self.route("/api/g_mtcm/intelygenz").was_reached(timeout.GATEWAY),
        )


gateway_monitor_scenarios = [
    ReportIncident(),
]
