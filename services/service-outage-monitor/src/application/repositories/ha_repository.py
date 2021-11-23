from copy import deepcopy
from typing import List
from typing import Optional


class HaRepository:
    def __init__(self, logger, config):
        self._logger = logger
        self._config = config

    @staticmethod
    def is_ha_enabled(edge: dict) -> bool:
        return edge['edgeHASerialNumber'] is not None

    @staticmethod
    def is_ha_primary(edge: dict) -> bool:
        return edge['edgeIsHAPrimary'] is True

    @staticmethod
    def is_ha_standby(edge: dict) -> bool:
        return edge['edgeIsHAPrimary'] is False

    @staticmethod
    def is_raw_ha_state_under_monitoring(raw_ha_state: str) -> bool:
        return raw_ha_state in ('READY', 'FAILED')

    @staticmethod
    def normalize_raw_ha_state(raw_ha_state: str) -> Optional[str]:
        if raw_ha_state == 'READY':
            return 'CONNECTED'
        elif raw_ha_state == 'FAILED':
            return 'OFFLINE'
        else:
            return None

    def map_edges_with_ha_info(self, edges_with_links: List[dict], edges_with_ha_info: List[dict]) -> List[dict]:
        result = []

        edges_with_links_by_serial = {
            elem['edgeSerialNumber']: elem
            for elem in edges_with_links
        }
        edges_with_ha_info_by_serial = {
            elem['serialNumber']: elem
            for elem in edges_with_ha_info
        }

        for serial_number, edge_with_links in edges_with_links_by_serial.items():
            edge_ha_info = edges_with_ha_info_by_serial.get(serial_number)
            if not edge_ha_info:
                self._logger.info(f'No HA info was found for edge {serial_number}. Skipping...')
                continue

            ha_state = edge_ha_info['haState']
            if self.is_raw_ha_state_under_monitoring(ha_state):
                result.append({
                    **edge_with_links,
                    'edgeHAState': self.normalize_raw_ha_state(ha_state),
                    'edgeIsHAPrimary': True,
                })
            else:
                self._logger.info(
                    f'HA partner for {serial_number} is in state {ha_state}, so HA will be considered as disabled for '
                    'this edge'
                )
                result.append({
                    **edge_with_links,
                    'edgeHASerialNumber': None,
                    'edgeHAState': None,
                    'edgeIsHAPrimary': None,
                })

        return result

    def get_edges_with_standbys_as_standalone_edges(self, edges_with_ha_info: List[dict]) -> List[dict]:
        standby_edges = []

        for edge in edges_with_ha_info:
            if not self.is_ha_enabled(edge):
                continue

            copy = deepcopy(edge)
            copy['edgeState'], copy['edgeHAState'] = copy['edgeHAState'], copy['edgeState']
            copy['edgeSerialNumber'], copy['edgeHASerialNumber'] = copy['edgeHASerialNumber'], copy['edgeSerialNumber']
            copy['edgeIsHAPrimary'] = not copy['edgeIsHAPrimary']

            standby_edges.append(copy)

        return edges_with_ha_info + standby_edges
