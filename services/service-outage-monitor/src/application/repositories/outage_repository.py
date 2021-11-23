import re
from typing import List
from typing import Optional

from application import Outages


class OutageRepository:
    def __init__(self, logger, ha_repository):
        self._logger = logger
        self._ha_repository = ha_repository

    def is_there_an_outage(self, edge_status):
        is_faulty_edge = self.is_faulty_edge(edge_status["edgeState"])
        is_there_any_faulty_link = any(
            self.is_faulty_link(link_status['linkState'])
            for link_status in edge_status['links']
        )

        return is_faulty_edge or is_there_any_faulty_link

    def is_faulty_edge(self, edge_state: str):
        return edge_state == 'OFFLINE'

    def is_faulty_link(self, link_state: str):
        return link_state == 'DISCONNECTED'

    def _is_link_wired(self, link, links_configuration):
        link_type = ''
        for link_configuration in links_configuration:
            if link['interface'] in link_configuration['interfaces']:
                link_type = link_configuration['type']
                break
        return link_type == 'WIRED'

    def is_any_link_disconnected(self, links: list) -> bool:
        return any(self.find_disconnected_links(links))

    def find_disconnected_links(self, links: list) -> list:
        return [link for link in links if self.is_faulty_link(link['linkState'])]

    def find_disconnected_wired_links(self, edge_status, links_configuration):
        return [
            link
            for link in edge_status['links']
            if self._is_link_wired(link, links_configuration)
            if self.is_faulty_link(link['linkState'])
        ]

    def is_outage_ticket_detail_auto_resolvable(self, ticket_notes: list,
                                                serial_number: str,
                                                max_autoresolves: int) -> bool:
        regex = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nAuto-resolving detail for serial")
        times_autoresolved = 0

        for ticket_note in ticket_notes:
            note_value = ticket_note['noteValue']
            is_autoresolve_note = bool(regex.match(note_value))
            is_note_related_to_serial = serial_number in ticket_note['serviceNumber']
            times_autoresolved += int(is_autoresolve_note and is_note_related_to_serial)

            if times_autoresolved >= max_autoresolves:
                return False

        return True

    def filter_edges_by_outage_type(self, edges_info: List[dict], outage_type: Outages) -> List[dict]:
        filter_fn = None
        if outage_type is Outages.LINK_DOWN:
            filter_fn = self.is_link_down_outage
        elif outage_type is Outages.HARD_DOWN:
            filter_fn = self.is_hard_down_outage
        elif outage_type is Outages.HA_LINK_DOWN:
            filter_fn = self.is_ha_link_down_outage
        elif outage_type is Outages.HA_SOFT_DOWN:
            filter_fn = self.is_ha_soft_down_outage
        elif outage_type is Outages.HA_HARD_DOWN:
            filter_fn = self.is_ha_hard_down_outage

        return [edge for edge in edges_info if filter_fn(edge['status'])]

    def get_outage_type_by_edge_status(self, edge_status: dict) -> Optional[Outages]:
        if self.is_link_down_outage(edge_status):
            return Outages.LINK_DOWN
        elif self.is_hard_down_outage(edge_status):
            return Outages.HARD_DOWN
        elif self.is_ha_link_down_outage(edge_status):
            return Outages.HA_LINK_DOWN
        elif self.is_ha_soft_down_outage(edge_status):
            return Outages.HA_SOFT_DOWN
        elif self.is_ha_hard_down_outage(edge_status):
            return Outages.HA_HARD_DOWN
        else:
            return None

    def should_document_outage(self, edge_status: dict) -> bool:
        outage_type = self.get_outage_type_by_edge_status(edge_status)
        is_ha_primary = self._ha_repository.is_ha_primary(edge_status)

        if outage_type in (Outages.HA_LINK_DOWN, Outages.HA_HARD_DOWN) and not is_ha_primary:
            # Hard and Link Downs with HA enabled must always be documented for the primary edge in the pair
            return False
        else:
            return True

    def is_link_down_outage(self, edge_status: dict) -> bool:
        # Link Down Outage (HA disabled): any link is DOWN and the edge is UP
        any_link_down = self.is_any_link_disconnected(edge_status['links'])
        is_edge_up = not self.is_faulty_edge(edge_status['edgeState'])
        is_ha_disabled = not self._ha_repository.is_ha_enabled(edge_status)

        return any_link_down and is_edge_up and is_ha_disabled

    def is_ha_link_down_outage(self, edge_status: dict) -> bool:
        # Link Down Outage (HA enabled): any link is DOWN and at least one edge in the HA pair is UP
        any_link_down = self.is_any_link_disconnected(edge_status['links'])
        is_edge_up = not self.is_faulty_edge(edge_status['edgeState'])
        is_ha_enabled = self._ha_repository.is_ha_enabled(edge_status)
        is_ha_partner_up = not self.is_faulty_edge(edge_status['edgeHAState'])

        return any_link_down and is_ha_enabled and (is_edge_up or is_ha_partner_up)

    def is_ha_soft_down_outage(self, edge_status: dict) -> bool:
        # Soft Down Outage (HA enabled): all links are UP and only the current edge is DOWN in the HA pair
        is_ha_enabled = self._ha_repository.is_ha_enabled(edge_status)
        is_ha_partner_up = not self.is_faulty_edge(edge_status['edgeHAState'])
        all_links_up = not self.is_any_link_disconnected(edge_status['links'])
        is_edge_down = self.is_faulty_edge(edge_status['edgeState'])

        return is_ha_enabled and is_ha_partner_up and all_links_up and is_edge_down

    def is_hard_down_outage(self, edge_status: dict) -> bool:
        # Hard Down Outage (HA disabled): current edge is DOWN
        is_edge_down = self.is_faulty_edge(edge_status['edgeState'])
        is_ha_disabled = not self._ha_repository.is_ha_enabled(edge_status)

        return is_edge_down and is_ha_disabled

    def is_ha_hard_down_outage(self, edge_status: dict) -> bool:
        # Hard Down Outage (HA enabled): both edges in the HA pair are DOWN
        is_edge_down = self.is_faulty_edge(edge_status['edgeState'])
        is_ha_enabled = self._ha_repository.is_ha_enabled(edge_status)
        is_ha_partner_down = self.is_faulty_edge(edge_status['edgeHAState'])

        return is_edge_down and is_ha_enabled and is_ha_partner_down

    def is_edge_up(self, edge_status: dict) -> bool:
        # No Outage Detected: current edge and all its links are UP
        is_edge_up = not self.is_faulty_edge(edge_status['edgeState'])
        all_links_up = not self.is_any_link_disconnected(edge_status['links'])

        return is_edge_up and all_links_up
