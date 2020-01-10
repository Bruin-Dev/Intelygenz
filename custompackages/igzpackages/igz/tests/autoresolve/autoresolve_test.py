import json
import pytest

from unittest.mock import Mock

from igz.packages.autoresolve import AutoResolve


class TestAutoResolve:

    def is_there_an_outage_edge_test(self):
        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_status_1 = {
            'edges': {'edgeState': edge_1_state, 'serialNumber': 'VC1234567'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_1_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_1_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_2_state = 'OFFLINE'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'DISCONNECTED'
        edge_status_2 = {
            'edges': {'edgeState': edge_2_state, 'serialNumber': 'VC7654321'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_2_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_2_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_ge1_state = 'STABLE'
        edge_3_link_ge2_state = 'DISCONNECTED'
        edge_status_3 = {
            'edges': {'edgeState': edge_3_state, 'serialNumber': 'VC1112223'},
            'links': [
                {'linkId': 1234, 'link': {'state': edge_3_link_ge1_state, 'interface': 'GE1'}},
                {'linkId': 5678, 'link': {'state': edge_3_link_ge2_state, 'interface': 'GE2'}},
            ],
            'enterprise_name': 'EVIL-CORP|12345|',
        }

        logger = Mock()

        auto_resolve = AutoResolve(logger=logger)

        result = auto_resolve._is_there_an_outage(edge_status_1)
        assert result is False

        result = auto_resolve._is_there_an_outage(edge_status_2)
        assert result is True

        result = auto_resolve._is_there_an_outage(edge_status_3)
        assert result is True

    def is_faulty_edge_test(self):
        edge_state_1 = 'CONNECTED'
        edge_state_2 = 'OFFLINE'

        logger = Mock()

        auto_resolve = AutoResolve(logger=logger)

        result = auto_resolve._is_faulty_edge(edge_state_1)
        assert result is False

        result = auto_resolve._is_faulty_edge(edge_state_2)
        assert result is True

    def is_faulty_link_test(self):
        link_state_1 = 'STABLE'
        link_state_2 = 'DISCONNECTED'

        logger = Mock()

        auto_resolve = AutoResolve(logger=logger)

        result = auto_resolve._is_faulty_link(link_state_1)
        assert result is False

        result = auto_resolve._is_faulty_link(link_state_2)
        assert result is True
