from unittest.mock import Mock

from application.repositories.ha_repository import HaRepository
from config import testconfig


class TestHaRepository:
    def instance_test(self, ha_repository, logger):
        assert ha_repository._logger is logger
        assert ha_repository._config is testconfig

    def is_ha_enabled_test(self):
        base_edge = {
            # Some fields omitted for simplicity
            "host": "mettel.velocloud.net",
            "enterpriseId": 1,
            "edgeName": "Big Boss",
            "edgeState": "CONNECTED",
            "edgeId": 1,
            "edgeSerialNumber": "VC1234567",
        }

        edge = {
            **base_edge,
            "edgeHASerialNumber": None,
        }
        result = HaRepository.is_ha_enabled(edge)
        assert result is False

        edge = {
            **base_edge,
            "edgeHASerialNumber": "VC9999999",
        }
        result = HaRepository.is_ha_enabled(edge)
        assert result is True

    def is_ha_primary_test(self):
        base_edge = {
            # Some fields omitted for simplicity
            "host": "mettel.velocloud.net",
            "enterpriseId": 1,
            "edgeName": "Big Boss",
            "edgeState": "CONNECTED",
            "edgeId": 1,
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "edgeHAState": "OFFLINE",
        }

        edge = {
            **base_edge,
            "edgeIsHAPrimary": False,
        }
        result = HaRepository.is_ha_primary(edge)
        assert result is False

        edge = {
            **base_edge,
            "edgeIsHAPrimary": True,
        }
        result = HaRepository.is_ha_primary(edge)
        assert result is True

    def is_ha_standby_test(self):
        base_edge = {
            # Some fields omitted for simplicity
            "host": "mettel.velocloud.net",
            "enterpriseId": 1,
            "edgeName": "Big Boss",
            "edgeState": "CONNECTED",
            "edgeId": 1,
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "edgeHAState": "OFFLINE",
        }

        edge = {
            **base_edge,
            "edgeIsHAPrimary": True,
        }
        result = HaRepository.is_ha_standby(edge)
        assert result is False

        edge = {
            **base_edge,
            "edgeIsHAPrimary": False,
        }
        result = HaRepository.is_ha_standby(edge)
        assert result is True

    def is_raw_ha_state_under_monitoring_test(self):
        raw_ha_state = "UNCONFIGURED"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is False

        raw_ha_state = "PENDING_INIT"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is False

        raw_ha_state = "PENDING_DISSOCIATION"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is False

        raw_ha_state = "PENDING_CONFIRMATION"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is False

        raw_ha_state = "PENDING_CONFIRMED"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is False

        raw_ha_state = "READY"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is True

        raw_ha_state = "FAILED"
        result = HaRepository.is_raw_ha_state_under_monitoring(raw_ha_state)
        assert result is True

    def normalize_raw_ha_state_test(self):
        raw_ha_state = "UNCONFIGURED"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is None

        raw_ha_state = "PENDING_INIT"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is None

        raw_ha_state = "PENDING_DISSOCIATION"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is None

        raw_ha_state = "PENDING_CONFIRMATION"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is None

        raw_ha_state = "PENDING_CONFIRMED"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is None

        raw_ha_state = "READY"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is "CONNECTED"

        raw_ha_state = "FAILED"
        result = HaRepository.normalize_raw_ha_state(raw_ha_state)
        assert result is "OFFLINE"

    def map_edges_with_ha_info_test(self):
        enterprise_id = 1

        edge_1_id = 1
        edge_1_serial = "VC1234567"
        edge_1_state = "CONNECTED"
        edge_1_ha_serial = "VC9999999"
        edge_1_ha_state = "READY"

        edge_2_id = 2
        edge_2_serial = "VC8901234"
        edge_2_state = "CONNECTED"
        edge_2_ha_serial = "VC88888888"
        edge_2_ha_state = "FAILED"

        edge_3_id = 3
        edge_3_serial = "VC5678901"
        edge_3_state = "OFFLINE"
        edge_3_ha_serial = None
        edge_3_ha_state = "UNCONFIGURED"

        edge_4_id = 4
        edge_4_serial = "VC2345678"
        edge_4_state = "CONNECTED"
        edge_4_ha_serial = "VC7777777"
        edge_4_ha_state = "PENDING_INIT"

        edge_5_id = 5
        edge_5_serial = "VC9012345"
        edge_5_state = "OFFLINE"
        edge_5_ha_serial = "VC6666666"
        edge_5_ha_state = "PENDING_CONFIRMATION"

        edge_6_id = 6
        edge_6_serial = "VC6789012"
        edge_6_state = "CONNECTED"
        edge_6_ha_serial = "VC6666666"
        edge_6_ha_state = "PENDING_CONFIRMED"

        edge_7_id = 7
        edge_7_serial = "VC3456789"
        edge_7_state = "OFFLINE"
        edge_7_ha_serial = "VC6666666"
        edge_7_ha_state = "PENDING_DISSOCIATION"

        edge_1 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_1_state,
            "edgeId": edge_1_id,
            "edgeSerialNumber": edge_1_serial,
            "edgeHASerialNumber": edge_1_ha_serial,
        }
        edge_2 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_2_state,
            "edgeId": edge_2_id,
            "edgeSerialNumber": edge_2_serial,
            "edgeHASerialNumber": edge_2_ha_serial,
        }
        edge_3 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_3_state,
            "edgeId": edge_3_id,
            "edgeSerialNumber": edge_3_serial,
            "edgeHASerialNumber": edge_3_ha_serial,
        }
        edge_4 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_4_state,
            "edgeId": edge_4_id,
            "edgeSerialNumber": edge_4_serial,
            "edgeHASerialNumber": edge_4_ha_serial,
        }
        edge_5 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_5_state,
            "edgeId": edge_5_id,
            "edgeSerialNumber": edge_5_serial,
            "edgeHASerialNumber": edge_5_ha_serial,
        }
        edge_6 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_6_state,
            "edgeId": edge_6_id,
            "edgeSerialNumber": edge_6_serial,
            "edgeHASerialNumber": edge_6_ha_serial,
        }
        edge_7 = {
            # Some fields omitted for simplicity
            "enterpriseId": enterprise_id,
            "edgeState": edge_7_state,
            "edgeId": edge_7_id,
            "edgeSerialNumber": edge_7_serial,
            "edgeHASerialNumber": edge_7_ha_serial,
        }
        edges = [
            edge_1,
            edge_2,
            edge_3,
            edge_4,
            edge_5,
            edge_6,
            edge_7,
        ]

        edges_with_ha_info = [
            {
                # Some fields omitted for simplicity
                "edgeState": edge_1_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_1_ha_serial,
                "haState": edge_1_ha_state,
                "id": edge_1_id,
                "serialNumber": edge_1_serial,
            },
            {
                # Some fields omitted for simplicity
                "edgeState": edge_2_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_2_ha_serial,
                "haState": edge_2_ha_state,
                "id": edge_2_id,
                "serialNumber": edge_2_serial,
            },
            {
                # Some fields omitted for simplicity
                "edgeState": edge_3_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_3_ha_serial,
                "haState": edge_3_ha_state,
                "id": edge_3_id,
                "serialNumber": edge_3_serial,
            },
            {
                # Some fields omitted for simplicity
                "edgeState": edge_4_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_4_ha_serial,
                "haState": edge_4_ha_state,
                "id": edge_4_id,
                "serialNumber": edge_4_serial,
            },
            {
                # Some fields omitted for simplicity
                "edgeState": edge_5_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_5_ha_serial,
                "haState": edge_5_ha_state,
                "id": edge_5_id,
                "serialNumber": edge_5_serial,
            },
            {
                # Some fields omitted for simplicity
                "edgeState": edge_6_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_6_ha_serial,
                "haState": edge_6_ha_state,
                "id": edge_6_id,
                "serialNumber": edge_6_serial,
            },
            {
                # Some fields omitted for simplicity
                "edgeState": edge_7_state,
                "enterpriseId": enterprise_id,
                "haSerialNumber": edge_7_ha_serial,
                "haState": edge_7_ha_state,
                "id": edge_7_id,
                "serialNumber": edge_7_serial,
            },
        ]

        logger = Mock()
        config = testconfig

        ha_repository = HaRepository(logger, config)

        result = ha_repository.map_edges_with_ha_info(edges, edges_with_ha_info)

        expected = [
            {
                **edge_1,
                "edgeHAState": "CONNECTED",
                "edgeIsHAPrimary": True,
            },
            {
                **edge_2,
                "edgeHAState": "OFFLINE",
                "edgeIsHAPrimary": True,
            },
            {
                **edge_3,
                "edgeHASerialNumber": None,
                "edgeHAState": None,
                "edgeIsHAPrimary": None,
            },
            {
                **edge_4,
                "edgeHASerialNumber": None,
                "edgeHAState": None,
                "edgeIsHAPrimary": None,
            },
            {
                **edge_5,
                "edgeHASerialNumber": None,
                "edgeHAState": None,
                "edgeIsHAPrimary": None,
            },
            {
                **edge_6,
                "edgeHASerialNumber": None,
                "edgeHAState": None,
                "edgeIsHAPrimary": None,
            },
            {
                **edge_7,
                "edgeHASerialNumber": None,
                "edgeHAState": None,
                "edgeIsHAPrimary": None,
            },
        ]
        assert result == expected

    def get_edges_with_standbys_as_standalone_edges_test(self):
        edge_1 = {
            # Some fields omitted for simplicity
            "enterpriseId": 1,
            "edgeState": "CONNECTED",
            "edgeId": 1,
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "edgeHAState": "OFFLINE",
            "edgeIsHAPrimary": True,
        }
        edge_2 = {
            # Some fields omitted for simplicity
            "enterpriseId": 1,
            "edgeState": "OFFLINE",
            "edgeId": 2,
            "edgeSerialNumber": "VC8901234",
            "edgeHASerialNumber": None,
            "edgeHAState": None,
            "edgeIsHAPrimary": None,
        }
        edges = [
            edge_1,
            edge_2,
        ]

        logger = Mock()
        config = testconfig

        ha_repository = HaRepository(logger, config)

        result = ha_repository.get_edges_with_standbys_as_standalone_edges(edges)

        edge_1_ha_partner = {
            # Some fields omitted for simplicity
            "enterpriseId": 1,
            "edgeState": "OFFLINE",
            "edgeId": 1,
            "edgeSerialNumber": "VC9999999",
            "edgeHASerialNumber": "VC1234567",
            "edgeHAState": "CONNECTED",
            "edgeIsHAPrimary": False,
        }
        expected = [
            edge_1,
            edge_2,
            edge_1_ha_partner,
        ]
        assert result == expected
