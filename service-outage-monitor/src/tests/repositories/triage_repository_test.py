import os

from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from application.repositories import triage_repository as triage_repository_module
from application.repositories.triage_repository import TriageRepository
from application.repositories.utils_repository import UtilsRepository
from config import testconfig


class TestTriageRepository:
    @pytest.mark.asyncio
    async def build_triage_note_with_no_missing_data_test(self):
        edge_serial = 'VC1234567'
        host = 'some-host'
        enterprise_id = 100
        edge_id = 200

        links_configuration = [
            {
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE7"
                ],
                "lastActive": 1565622307499,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PUBLIC",
                "type": "WIRED",
                "interfaces": [
                    "GE1"
                ],
                "lastActive": 1580508612156,
            },
            {
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "mode": "PRIVATE",
                "type": "WIRED",
                "interfaces": [
                    "INTERNET3"
                ],
                "lastActive": 1580508612156,
            }
        ]
        cached_edge = {
            'edge':
                {
                    'host': 'some-host',
                    'enterprise_id': 100,
                    'edge_id': 200},
            'links_configuration': links_configuration
        }
        edge_status_1 = {
            'edgeState': 'OFFLINE',
            'edgeName': 'Travis Touchdown',
            'edgeSerialNumber': edge_serial,
            'enterpriseName': 'EVIL-CORP|12345|',
            'host': host,
            'enterpriseId': enterprise_id,
            'edgeId': edge_id,
            "links": [
                {
                    'linkId': 1234,
                    'linkState': 'DISCONNECTED',
                    'interface': 'GE1',
                    'displayName': 'Solid Snake',

                },
                {
                    'linkId': 9012,
                    'linkState': 'STABLE',
                    'interface': 'GE7',
                    'displayName': 'Big Boss',
                },
                {
                    'linkId': 5678,
                    'linkState': 'STABLE',
                    'interface': 'INTERNET3',
                    'displayName': 'Otacon',
                }
            ]
        }

        event_1 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 00:40:00+00:00',
            'message': 'Link GE7 is now DEAD'
        }
        event_2 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 01:40:00+00:00',
            'message': 'Link GE1 is now DEAD'
        }
        event_3 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-30 02:40:00+00:00',
            'message': 'Link GE1 is no longer DEAD'
        }
        event_4 = {
            'event': 'EDGE_NEW_DEVICE',
            'category': 'EDGE',
            'eventTime': '2019-07-30 03:40:00+00:00',
            'message': 'New or updated client device'
        }
        event_5 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'SYSTEM',
            'eventTime': '2019-07-29 04:40:00+00:00',
            'message': 'Interface GE1 is up'
        }
        event_6 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-31 05:40:00+00:00',
            'message': 'Link GE7 is now DEAD'
        }
        event_7 = {
            'event': 'EDGE_INTERFACE_DOWN',
            'category': 'SYSTEM',
            'eventTime': '2019-07-28 06:40:00+00:00',
            'message': 'Interface GE7 is down'
        }
        event_8 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-01 07:40:00+00:00',
            'message': 'Link GE7 is no longer DEAD'
        }
        event_9 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 08:40:00+00:00',
            'message': 'Interface INTERNET3 is up'
        }
        event_10 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 09:40:00+00:00',
            'message': 'Link INTERNET3 is no longer DEAD'
        }
        event_11 = {
            'event': 'EDGE_UP',
            'category': 'EDGE',
            'eventTime': '2019-08-01 10:40:00+00:00',
            'message': 'Edge is up'
        }
        event_12 = {
            'event': 'EDGE_DOWN',
            'category': 'EDGE',
            'eventTime': '2019-08-01 11:40:00+00:00',
            'message': 'Edge is down'
        }
        events = [
            event_1, event_2, event_3, event_4, event_5,
            event_6, event_7, event_8, event_9, event_10,
            event_11, event_12,
        ]
        logger = Mock()
        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(logger=logger, config=config, utils_repository=utils_repository)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['timezone'] = 'UTC'

        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            triage_note = triage_repository.build_triage_note(cached_edge, edge_status_1, events)

        assert triage_note == os.linesep.join([
            "#*MetTel's IPA*#",
            'Triage (VeloCloud)',
            'Orchestrator Instance: some-host',
            'Edge Name: Travis Touchdown',
            'Links: [Edge|https://some-host/#!/operator/customer/100/monitor/edge/200/] - '
            '[QoE|https://some-host/#!/operator/customer/100/monitor/edge/200/qoe/] - '
            '[Transport|https://some-host/#!/operator/customer/100/monitor/edge/200/links/] - '
            '[Events|https://some-host/#!/operator/customer/100/monitor/events/]',
            'Serial: VC1234567',
            '',
            'Edge Status: OFFLINE',
            'Last Edge Online: 2019-08-01 10:40:00+00:00',
            'Last Edge Offline: 2019-08-01 11:40:00+00:00',
            '',
            'Interface GE1',
            'Interface GE1 Label: Solid Snake',
            'Interface GE1 Type: Public Wired',
            'Interface GE1 Status: DISCONNECTED',
            'Last GE1 Interface Online: 2019-07-30 02:40:00+00:00',
            'Last GE1 Interface Offline: 2019-07-30 01:40:00+00:00',
            '',
            'Interface GE7',
            'Interface GE7 Label: Big Boss',
            'Interface GE7 Type: Public Wired',
            'Interface GE7 Status: STABLE',
            'Last GE7 Interface Online: 2019-07-01 07:40:00+00:00',
            'Last GE7 Interface Offline: 2019-07-30 00:40:00+00:00',
            '',
            'Interface INTERNET3',
            'Interface INTERNET3 Label: Otacon',
            'Interface INTERNET3 Type: Private Wired',
            'Interface INTERNET3 Status: STABLE',
            'Last INTERNET3 Interface Online: 2019-08-01 09:40:00+00:00',
            'Last INTERNET3 Interface Offline: Unknown',
        ])

    def build_events_note_test(self):
        event_1 = {
            'event': 'EDGE_NEW_DEVICE',
            'category': 'EDGE',
            'eventTime': '2019-07-30 07:38:00+00:00',
            'message': 'New or updated client device'
        }
        event_2 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'SYSTEM',
            'eventTime': '2019-07-29 07:38:00+00:00',
            'message': 'Interface GE1 is up'
        }
        event_3 = {
            'event': 'LINK_DEAD',
            'category': 'NETWORK',
            'eventTime': '2019-07-31 07:38:00+00:00',
            'message': 'Link GE2 is now DEAD'
        }
        event_4 = {
            'event': 'EDGE_INTERFACE_DOWN',
            'category': 'SYSTEM',
            'eventTime': '2019-07-28 07:38:00+00:00',
            'message': 'Interface GE2 is down'
        }
        event_5 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-07-01 07:38:00+00:00',
            'message': 'Link GE2 is no longer DEAD'
        }
        event_6 = {
            'event': 'EDGE_INTERFACE_UP',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 07:38:00+00:00',
            'message': 'Interface INTERNET3 is up'
        }
        event_7 = {
            'event': 'LINK_ALIVE',
            'category': 'NETWORK',
            'eventTime': '2019-08-01 07:40:00+00:00',
            'message': 'Link INTERNET3 is no longer DEAD'
        }
        events = [event_1, event_2, event_3, event_4, event_5, event_6, event_7]

        logger = Mock()
        config = testconfig
        utils_repository = UtilsRepository()

        triage_repository = TriageRepository(logger=logger, config=config, utils_repository=utils_repository)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['timezone'] = 'UTC'

        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            events_note = triage_repository.build_events_note(events)

        assert events_note == os.linesep.join([
            "#*MetTel's IPA*#",
            'Triage (VeloCloud)',
            '',
            'New event: EDGE_NEW_DEVICE',
            'Device: Edge',
            'Event time: 2019-07-30 07:38:00+00:00',
            '',
            'New event: EDGE_INTERFACE_UP',
            'Device: Interface GE1',
            'Event time: 2019-07-29 07:38:00+00:00',
            '',
            'New event: LINK_DEAD',
            'Device: Interface GE2',
            'Event time: 2019-07-31 07:38:00+00:00',
            '',
            'New event: EDGE_INTERFACE_DOWN',
            'Device: Interface GE2',
            'Event time: 2019-07-28 07:38:00+00:00',
            '',
            'New event: LINK_ALIVE',
            'Device: Interface GE2',
            'Event time: 2019-07-01 07:38:00+00:00',
            '',
            'New event: EDGE_INTERFACE_UP',
            'Device: Interface INTERNET3',
            'Event time: 2019-08-01 07:38:00+00:00',
            '',
            'New event: LINK_ALIVE',
            'Device: Interface INTERNET3',
            'Event time: 2019-08-01 07:40:00+00:00',
            '',
            'Timestamp: 2019-08-01 07:40:00+00:00',
        ])
