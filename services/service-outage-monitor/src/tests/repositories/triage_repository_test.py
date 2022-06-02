import os
from datetime import datetime
from unittest.mock import Mock, patch

from application import Outages
from application.repositories import triage_repository as triage_repository_module
from application.repositories.triage_repository import TriageRepository
from application.repositories.utils_repository import UtilsRepository
from config import testconfig


class TestTriageRepository:
    def instance_test(self, triage_repository, utils_repository):
        assert triage_repository._utils_repository is utils_repository
        assert triage_repository._config is testconfig

    def build_triage_note_for_link_down_outage_test(self):
        outage_type = Outages.LINK_DOWN

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "CONNECTED",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": None,
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "DISCONNECTED",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "STABLE",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "STABLE",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": None,
            "edgeIsHAPrimary": None,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        with patch.object(config, "TIMEZONE", "UTC"):
            triage_note = triage_repository.build_triage_note(cached_edge, edge_status, events, outage_type)

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "Outage Type: Link Down (no HA)",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Serial: VC1234567",
                "Edge Status: CONNECTED",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: DISCONNECTED",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: STABLE",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: STABLE",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_triage_note_for_hard_down_outage_test(self):
        outage_type = Outages.HARD_DOWN

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "OFFLINE",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": None,
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "DISCONNECTED",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "DISCONNECTED",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "DISCONNECTED",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": None,
            "edgeIsHAPrimary": None,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        with patch.object(config, "TIMEZONE", "UTC"):
            triage_note = triage_repository.build_triage_note(cached_edge, edge_status, events, outage_type)

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "Outage Type: Hard Down (no HA)",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Serial: VC1234567",
                "Edge Status: OFFLINE",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: DISCONNECTED",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: DISCONNECTED",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: DISCONNECTED",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_triage_note_for_HA_link_down_outage_test(self):
        outage_type = Outages.HA_LINK_DOWN

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "CONNECTED",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "DISCONNECTED",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "STABLE",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "STABLE",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": "CONNECTED",
            "edgeIsHAPrimary": True,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(triage_repository_module, "datetime", new=datetime_mock):
            with patch.object(config, "TIMEZONE", "UTC"):
                triage_note = triage_repository.build_triage_note(cached_edge, edge_status, events, outage_type)

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "Outage Type: Link Down (HA)",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Serial: VC1234567",
                "Edge Status: CONNECTED",
                "HA Role: Primary",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Serial: VC9999999",
                "Edge Status: STANDBY READY",
                "HA Role: Standby",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: DISCONNECTED",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: STABLE",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: STABLE",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_triage_note_for_HA_soft_down_outage_test(self):
        outage_type = Outages.HA_SOFT_DOWN

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "CONNECTED",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "STABLE",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "STABLE",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "STABLE",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": "OFFLINE",
            "edgeIsHAPrimary": True,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(triage_repository_module, "datetime", new=datetime_mock):
            with patch.object(config, "TIMEZONE", "UTC"):
                triage_note = triage_repository.build_triage_note(cached_edge, edge_status, events, outage_type)

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "Outage Type: Soft Down (HA)",
                "High Availability - Edge Offline",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Serial: VC1234567",
                "Edge Status: CONNECTED",
                "HA Role: Primary",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Serial: VC9999999",
                "Edge Status: OFFLINE",
                "HA Role: Standby",
                f"Timestamp: {str(current_datetime)}",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: STABLE",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: STABLE",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: STABLE",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_triage_note_for_HA_hard_down_outage_test(self):
        outage_type = Outages.HA_HARD_DOWN

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "OFFLINE",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "DISCONNECTED",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "DISCONNECTED",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "DISCONNECTED",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": "OFFLINE",
            "edgeIsHAPrimary": True,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(triage_repository_module, "datetime", new=datetime_mock):
            with patch.object(config, "TIMEZONE", "UTC"):
                triage_note = triage_repository.build_triage_note(cached_edge, edge_status, events, outage_type)

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "Outage Type: Hard Down (HA)",
                "High Availability - Location Offline",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Both primary and secondary edges are DISCONNECTED.",
                "",
                "Serial: VC1234567",
                "Edge Status: OFFLINE",
                "HA Role: Primary",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Serial: VC9999999",
                "Edge Status: OFFLINE",
                "HA Role: Standby",
                f"Timestamp: {str(current_datetime)}",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: DISCONNECTED",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: DISCONNECTED",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: DISCONNECTED",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_triage_note_for_reopen_test(self):
        outage_type = Outages.LINK_DOWN  # We can use whatever outage type

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "CONNECTED",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": None,
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "DISCONNECTED",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "STABLE",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "STABLE",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": None,
            "edgeIsHAPrimary": None,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        with patch.object(config, "TIMEZONE", "UTC"):
            triage_note = triage_repository.build_triage_note(
                cached_edge, edge_status, events, outage_type, is_reopen_note=True
            )

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Re-opening ticket.",
                "",
                "Outage Type: Link Down (no HA)",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Serial: VC1234567",
                "Edge Status: CONNECTED",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: DISCONNECTED",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: STABLE",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: STABLE",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_triage_note_for_no_outage_test(self):
        outage_type = None

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE7"],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": ["INTERNET3"],
                "lastActive": 1580508612156,
            },
        ]
        cached_edge = {
            # Some fields omitted for simplicity
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 200},
            "links_configuration": links_configuration,
        }

        edge_status = {
            # Some fields omitted for simplicity
            "edgeState": "CONNECTED",
            "edgeName": "Travis Touchdown",
            "edgeSerialNumber": "VC1234567",
            "edgeHASerialNumber": "VC9999999",
            "host": "mettel.velocloud.net",
            "enterpriseId": 100,
            "edgeId": 200,
            "links": [
                {
                    # Some fields omitted for simplicity
                    "linkId": 1234,
                    "linkState": "DISCONNECTED",
                    "interface": "GE1",
                    "displayName": "Solid Snake",
                    "linkIpAddress": "86.16.6.1",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 9012,
                    "linkState": "DISCONNECTED",
                    "interface": "GE7",
                    "displayName": "Big Boss",
                    "linkIpAddress": "86.16.6.2",
                },
                {
                    # Some fields omitted for simplicity
                    "linkId": 5678,
                    "linkState": "DISCONNECTED",
                    "interface": "INTERNET3",
                    "displayName": "Otacon",
                    "linkIpAddress": "86.16.6.3",
                },
            ],
            "edgeHAState": "CONNECTED",
            "edgeIsHAPrimary": True,
        }

        event_1 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 00:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_2 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-30 01:40:00+00:00",
            "message": "Link GE1 is now DEAD",
        }
        event_3 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-30 02:40:00+00:00",
            "message": "Link GE1 is no longer DEAD",
        }
        event_4 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 03:40:00+00:00",
            "message": "New or updated client device",
        }
        event_5 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 04:40:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_6 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 05:40:00+00:00",
            "message": "Link GE7 is now DEAD",
        }
        event_7 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 06:40:00+00:00",
            "message": "Interface GE7 is down",
        }
        event_8 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:40:00+00:00",
            "message": "Link GE7 is no longer DEAD",
        }
        event_9 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 08:40:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_10 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 09:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        event_11 = {
            "event": "EDGE_UP",
            "category": "EDGE",
            "eventTime": "2019-08-01 10:40:00+00:00",
            "message": "Edge is up",
        }
        event_12 = {
            "event": "EDGE_DOWN",
            "category": "EDGE",
            "eventTime": "2019-08-01 11:40:00+00:00",
            "message": "Edge is down",
        }
        events = [
            event_1,
            event_2,
            event_3,
            event_4,
            event_5,
            event_6,
            event_7,
            event_8,
            event_9,
            event_10,
            event_11,
            event_12,
        ]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        current_datetime = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(triage_repository_module, "datetime", new=datetime_mock):
            with patch.object(config, "TIMEZONE", "UTC"):
                triage_note = triage_repository.build_triage_note(cached_edge, edge_status, events, outage_type)

        assert triage_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "Orchestrator Instance: mettel.velocloud.net",
                "Edge Name: Travis Touchdown",
                "Links: [Edge|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/] - "
                "[QoE|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/qoe/] - "
                "[Transport|https://mettel.velocloud.net/#!/operator/customer/100/monitor/edge/200/links/] - "
                "[Events|https://mettel.velocloud.net/#!/operator/customer/100/monitor/events/]",
                "",
                "Serial: VC1234567",
                "Edge Status: CONNECTED",
                "HA Role: Primary",
                "Last Edge Online: 2019-08-01 10:40:00+00:00",
                "Last Edge Offline: 2019-08-01 11:40:00+00:00",
                "",
                "Serial: VC9999999",
                "Edge Status: STANDBY READY",
                "HA Role: Standby",
                "",
                "Interface GE1",
                "Interface GE1 Label: Solid Snake",
                "Interface GE1 IP Address: 86.16.6.1",
                "Interface GE1 Type: Public Wired",
                "Interface GE1 Status: DISCONNECTED",
                "Last GE1 Interface Online: 2019-07-30 02:40:00+00:00",
                "Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00",
                "",
                "Interface GE7",
                "Interface GE7 Label: Big Boss",
                "Interface GE7 IP Address: 86.16.6.2",
                "Interface GE7 Type: Public Wired",
                "Interface GE7 Status: DISCONNECTED",
                "Last GE7 Interface Online: 2019-07-01 07:40:00+00:00",
                "Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00",
                "",
                "Interface INTERNET3",
                "Interface INTERNET3 Label: Otacon",
                "Interface INTERNET3 IP Address: 86.16.6.3",
                "Interface INTERNET3 Type: Private Wired",
                "Interface INTERNET3 Status: DISCONNECTED",
                "Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00",
                "Last INTERNET3 Interface Offline: Unknown",
            ]
        )

    def build_events_note_test(self):
        event_1 = {
            "event": "EDGE_NEW_DEVICE",
            "category": "EDGE",
            "eventTime": "2019-07-30 07:38:00+00:00",
            "message": "New or updated client device",
        }
        event_2 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "SYSTEM",
            "eventTime": "2019-07-29 07:38:00+00:00",
            "message": "Interface GE1 is up",
        }
        event_3 = {
            "event": "LINK_DEAD",
            "category": "NETWORK",
            "eventTime": "2019-07-31 07:38:00+00:00",
            "message": "Link GE2 is now DEAD",
        }
        event_4 = {
            "event": "EDGE_INTERFACE_DOWN",
            "category": "SYSTEM",
            "eventTime": "2019-07-28 07:38:00+00:00",
            "message": "Interface GE2 is down",
        }
        event_5 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-07-01 07:38:00+00:00",
            "message": "Link GE2 is no longer DEAD",
        }
        event_6 = {
            "event": "EDGE_INTERFACE_UP",
            "category": "NETWORK",
            "eventTime": "2019-08-01 07:38:00+00:00",
            "message": "Interface INTERNET3 is up",
        }
        event_7 = {
            "event": "LINK_ALIVE",
            "category": "NETWORK",
            "eventTime": "2019-08-01 07:40:00+00:00",
            "message": "Link INTERNET3 is no longer DEAD",
        }
        events = [event_1, event_2, event_3, event_4, event_5, event_6, event_7]

        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(config=config, utils_repository=utils_repository)

        with patch.object(config, "TIMEZONE", "UTC"):
            events_note = triage_repository.build_events_note(events)

        assert events_note == os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (VeloCloud)",
                "",
                "New event: EDGE_NEW_DEVICE",
                "Device: Edge",
                "Event time: 2019-07-30 07:38:00+00:00",
                "",
                "New event: EDGE_INTERFACE_UP",
                "Device: Interface GE1",
                "Event time: 2019-07-29 07:38:00+00:00",
                "",
                "New event: LINK_DEAD",
                "Device: Interface GE2",
                "Event time: 2019-07-31 07:38:00+00:00",
                "",
                "New event: EDGE_INTERFACE_DOWN",
                "Device: Interface GE2",
                "Event time: 2019-07-28 07:38:00+00:00",
                "",
                "New event: LINK_ALIVE",
                "Device: Interface GE2",
                "Event time: 2019-07-01 07:38:00+00:00",
                "",
                "New event: EDGE_INTERFACE_UP",
                "Device: Interface INTERNET3",
                "Event time: 2019-08-01 07:38:00+00:00",
                "",
                "New event: LINK_ALIVE",
                "Device: Interface INTERNET3",
                "Event time: 2019-08-01 07:40:00+00:00",
                "",
                "Timestamp: 2019-08-01 07:40:00+00:00",
            ]
        )
