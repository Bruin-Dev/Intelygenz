from unittest.mock import Mock

from application import Outages
from application.repositories.outage_repository import OutageRepository


class TestOutageRepository:
    def instance_test(self):
        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)

        assert outage_repository._logger is logger
        assert outage_repository._ha_repository is ha_repository

    def is_there_an_outage_edge_test(self):
        edge_1_state = 'CONNECTED'
        edge_1_link_ge1_state = edge_1_link_ge2_state = 'STABLE'
        edge_status_1 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_1_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_1_link_ge1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_1_link_ge2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_2_state = 'OFFLINE'
        edge_2_link_ge1_state = edge_2_link_ge2_state = 'DISCONNECTED'
        edge_status_2 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_2_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_2_link_ge1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_2_link_ge2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        edge_3_state = 'OFFLINE'
        edge_3_link_ge1_state = 'STABLE'
        edge_3_link_ge2_state = 'DISCONNECTED'
        edge_status_3 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_3_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_3_link_ge1_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': edge_3_link_ge2_state,
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        logger = Mock()
        ha_repository = Mock()

        outage_utils = OutageRepository(logger, ha_repository)

        result = outage_utils.is_there_an_outage(edge_status_1)
        assert result is False

        result = outage_utils.is_there_an_outage(edge_status_2)
        assert result is True

        result = outage_utils.is_there_an_outage(edge_status_3)
        assert result is True

    def is_any_link_disconnected_test(self):
        links_1 = [
            {
                'interface': 'REX',
                'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                'linkState': 'STABLE',
                'linkLastActive': '2020-09-29T04:45:15.000Z',
                'linkVpnState': 'STABLE',
                'linkId': 5293,
                'linkIpAddress': '70.59.5.185',
            },
            {
                'interface': 'RAY',
                'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                'linkState': 'DISCONNECTED',
                'linkLastActive': '2020-09-29T04:45:15.000Z',
                'linkVpnState': 'STABLE',
                'linkId': 5293,
                'linkIpAddress': '70.59.5.185',
            },
        ]
        links_2 = [
            {
                'interface': 'REX',
                'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                'linkState': 'STABLE',
                'linkLastActive': '2020-09-29T04:45:15.000Z',
                'linkVpnState': 'STABLE',
                'linkId': 5293,
                'linkIpAddress': '70.59.5.185',
            },
            {
                'interface': 'RAY',
                'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                'linkState': 'STABLE',
                'linkLastActive': '2020-09-29T04:45:15.000Z',
                'linkVpnState': 'STABLE',
                'linkId': 5293,
                'linkIpAddress': '70.59.5.185',
            },
        ]

        logger = Mock()
        ha_repository = Mock()

        outage_utils = OutageRepository(logger, ha_repository)

        result_1 = outage_utils.is_any_link_disconnected(links_1)
        result_2 = outage_utils.is_any_link_disconnected(links_2)

        assert result_1 is True
        assert result_2 is False

    def find_disconnected_wired_links_test(self):
        edge_status_1 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'DISCONNECTED',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'DISCONNECTED',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }
        edge_status_2 = {
            'host': 'mettel.velocloud.net',
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': 1,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': 'ONLINE',
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': 1,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': [
                {
                    'interface': 'REX',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'RAY',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
                {
                    'interface': 'REZZ',
                    'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
                    'linkState': 'STABLE',
                    'linkLastActive': '2020-09-29T04:45:15.000Z',
                    'linkVpnState': 'STABLE',
                    'linkId': 5293,
                    'linkIpAddress': '70.59.5.185',
                },
            ],
        }

        links_configuration = [
            {
                'interfaces': ['REX'],
                'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                'mode': 'PUBLIC',
                'type': 'WIRED',
                'last_active': '2020-09-29T04:45:15.000Z'
            },
            {
                'interfaces': ['RAY'],
                'internal_id': '00000001-ac48-47a0-81a7-80c8c320f486',
                'mode': 'PUBLIC',
                'type': 'WIRED',
                'last_active': '2020-09-29T04:45:15.000Z'
            }
        ]
        logger = Mock()
        ha_repository = Mock()

        outage_utils = OutageRepository(logger, ha_repository)

        result_1 = outage_utils.find_disconnected_wired_links(edge_status_1, links_configuration)
        result_2 = outage_utils.find_disconnected_wired_links(edge_status_2, links_configuration)

        assert result_1 == edge_status_1['links']
        assert result_2 == []

    def is_faulty_edge_test(self):
        edge_state_1 = 'CONNECTED'
        edge_state_2 = 'OFFLINE'

        logger = Mock()
        ha_repository = Mock()

        outage_utils = OutageRepository(logger, ha_repository)

        result = outage_utils.is_faulty_edge(edge_state_1)
        assert result is False

        result = outage_utils.is_faulty_edge(edge_state_2)
        assert result is True

    def is_faulty_link_test(self):
        link_state_1 = 'STABLE'
        link_state_2 = 'DISCONNECTED'

        logger = Mock()
        ha_repository = Mock()

        outage_utils = OutageRepository(logger, ha_repository)

        result = outage_utils.is_faulty_link(link_state_1)
        assert result is False

        result = outage_utils.is_faulty_link(link_state_2)
        assert result is True

    def find_disconnected_links_test(self):
        link_1 = {
            'interface': 'REX',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'STABLE',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }
        link_2 = {
            'interface': 'RAY',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': 'DISCONNECTED',
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }

        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)

        links = [
            link_1,
            link_2,
        ]
        result = outage_repository.find_disconnected_links(links)
        assert result == [link_2]

        links = [
            link_1,
        ]
        result = outage_repository.find_disconnected_links(links)
        assert result == []

    def is_outage_ticket_detail_auto_resolvable_test(self):
        serial_number_1 = 'VC1234567'
        serial_number_2 = 'VC7654321'

        text_identifier_old_watermark = (
            "#*Automation Engine*#\n"
            "Auto-resolving detail for serial\n"
        )

        text_identifier = ("#*MetTel's IPA*#\n"
                           "Auto-resolving detail for serial\n")

        note_value1 = f"{text_identifier}TimeStamp: 2021-01-02 10:18:16-05:00"
        note_value2 = f"{text_identifier_old_watermark}TimeStamp: 2020-01-02 10:18:16-05:00"
        note_value3 = f"{text_identifier}TimeStamp: 2022-01-02 10:18:16-05:00"

        note_value4 = ("#*MetTel's IPA*#\n"
                       "Just another kind of note\n")

        ticket_notes1 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": note_value4,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
        ]

        ticket_notes2 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value4,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
        ]

        ticket_notes3 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": note_value4,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": note_value3,
                "serviceNumber": [
                    serial_number_1,
                ],
            }
        ]

        ticket_notes4 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
            {
                "noteId": 41894043,
                "noteValue": note_value3,
                "serviceNumber": [
                    serial_number_2,
                ],
            }
        ]

        ticket_notes5 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894040,
                "noteValue": note_value1,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_1,
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
                "serviceNumber": [
                    serial_number_2,
                ],
            },
        ]

        logger = Mock()
        ha_repository = Mock()
        outage_utils = OutageRepository(logger, ha_repository)
        autoresolve_limit = 3

        ticket_bool1 = outage_utils.is_outage_ticket_detail_auto_resolvable(
            ticket_notes1, serial_number_1, autoresolve_limit
        )
        assert ticket_bool1 is True

        ticket_bool2 = outage_utils.is_outage_ticket_detail_auto_resolvable(
            ticket_notes2, serial_number_1, autoresolve_limit
        )
        assert ticket_bool2 is True

        ticket_bool3 = outage_utils.is_outage_ticket_detail_auto_resolvable(
            ticket_notes3, serial_number_1, autoresolve_limit
        )
        assert ticket_bool3 is False

        ticket_bool4 = outage_utils.is_outage_ticket_detail_auto_resolvable(
            ticket_notes4, serial_number_2, autoresolve_limit
        )
        assert ticket_bool4 is False

        ticket_bool5 = outage_utils.is_outage_ticket_detail_auto_resolvable(
            ticket_notes5, serial_number_1, autoresolve_limit
        )
        assert ticket_bool5 is True

        ticket_bool6 = outage_utils.is_outage_ticket_detail_auto_resolvable(
            ticket_notes5, serial_number_2, autoresolve_limit
        )
        assert ticket_bool6 is True

    def filter_edges_by_outage_type__link_down_outages_detected_test(self):
        outage_type = Outages.LINK_DOWN

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC8901234'

        edge_1 = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 1,
                'edgeSerialNumber': edge_1_serial,
                'edgeHASerialNumber': None,
                'edgeHAState': None,
                'edgeIsHAPrimary': None,
                'links': [
                    {
                        'interface': 'REX',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edge_2 = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 2,
                'edgeSerialNumber': edge_2_serial,
                'edgeHASerialNumber': None,
                'edgeHAState': None,
                'edgeIsHAPrimary': None,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'STABLE',
                    },
                ],
            },
        }
        edges = [
            edge_1,
            edge_2,
        ]

        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)
        outage_repository.is_link_down_outage = Mock(side_effect=[
            True,
            False,
        ])

        result = outage_repository.filter_edges_by_outage_type(edges, outage_type)

        expected = [
            edge_1,
        ]
        assert result == expected

    def filter_edges_by_outage_type__hard_down_outages_detected_test(self):
        outage_type = Outages.HARD_DOWN

        edge_1_serial = 'VC1234567'
        edge_2_serial = 'VC8901234'

        edge_1 = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'OFFLINE',
                'edgeId': 1,
                'edgeSerialNumber': edge_1_serial,
                'edgeHASerialNumber': None,
                'edgeHAState': None,
                'edgeIsHAPrimary': None,
                'links': [
                    {
                        'interface': 'REX',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edge_2 = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 2,
                'edgeSerialNumber': edge_2_serial,
                'edgeHASerialNumber': None,
                'edgeHAState': None,
                'edgeIsHAPrimary': None,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'STABLE',
                    },
                ],
            },
        }
        edges = [
            edge_1,
            edge_2,
        ]

        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)
        outage_repository.is_hard_down_outage = Mock(side_effect=[
            True,
            False,
        ])

        result = outage_repository.filter_edges_by_outage_type(edges, outage_type)

        expected = [
            edge_1,
        ]
        assert result == expected

    def filter_edges_by_outage_type__HA_link_down_outages_detected_test(self):
        outage_type = Outages.HA_LINK_DOWN

        edge_1_serial = 'VC1234567'
        edge_2_primary_serial = 'VC1234567'
        edge_2_standby_serial = 'VC9999999'

        edge_1 = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 1,
                'edgeSerialNumber': edge_1_serial,
                'edgeHASerialNumber': None,
                'edgeHAState': None,
                'edgeIsHAPrimary': None,
                'links': [
                    {
                        'interface': 'REX',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edge_2_primary = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 2,
                'edgeSerialNumber': edge_2_primary_serial,
                'edgeHASerialNumber': edge_2_standby_serial,
                'edgeHAState': 'CONNECTED',
                'edgeIsHAPrimary': True,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edge_2_standby = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 2,
                'edgeSerialNumber': edge_2_standby_serial,
                'edgeHASerialNumber': edge_2_primary_serial,
                'edgeHAState': 'CONNECTED',
                'edgeIsHAPrimary': False,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edges = [
            edge_1,
            edge_2_primary,
            edge_2_standby,
        ]

        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)
        outage_repository.is_ha_link_down_outage = Mock(side_effect=[
            False,
            True,
            False,
        ])

        result = outage_repository.filter_edges_by_outage_type(edges, outage_type)

        expected = [
            edge_2_primary,
        ]
        assert result == expected

    def filter_edges_by_outage_type__HA_soft_down_outages_detected_test(self):
        outage_type = Outages.HA_SOFT_DOWN

        edge_1_primary_serial = 'VC1234567'
        edge_1_standby_serial = 'VC9999999'

        edge_1_primary = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'CONNECTED',
                'edgeId': 2,
                'edgeSerialNumber': edge_1_primary_serial,
                'edgeHASerialNumber': edge_1_standby_serial,
                'edgeHAState': 'OFFLINE',
                'edgeIsHAPrimary': True,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'STABLE',
                    },
                ],
            },
        }
        edge_1_standby = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'OFFLINE',
                'edgeId': 2,
                'edgeSerialNumber': edge_1_standby_serial,
                'edgeHASerialNumber': edge_1_primary_serial,
                'edgeHAState': 'CONNECTED',
                'edgeIsHAPrimary': False,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'STABLE',
                    },
                ],
            },
        }
        edges = [
            edge_1_primary,
            edge_1_standby,
        ]

        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)
        outage_repository.is_ha_soft_down_outage = Mock(side_effect=[
            False,
            True,
        ])

        result = outage_repository.filter_edges_by_outage_type(edges, outage_type)

        expected = [
            edge_1_standby,
        ]
        assert result == expected

    def filter_edges_by_outage_type__HA_hard_down_outages_detected_test(self):
        outage_type = Outages.HA_HARD_DOWN

        edge_1_primary_serial = 'VC1234567'
        edge_1_standby_serial = 'VC9999999'
        edge_2_serial = 'VC8901234'

        edge_1_primary = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'OFFLINE',
                'edgeId': 2,
                'edgeSerialNumber': edge_1_primary_serial,
                'edgeHASerialNumber': edge_1_standby_serial,
                'edgeHAState': 'OFFLINE',
                'edgeIsHAPrimary': True,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edge_1_standby = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'OFFLINE',
                'edgeId': 2,
                'edgeSerialNumber': edge_1_standby_serial,
                'edgeHASerialNumber': edge_1_primary_serial,
                'edgeHAState': 'OFFLINE',
                'edgeIsHAPrimary': False,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edge_2 = {
            'cached_info': {},  # We don't care about this
            'status': {
                # Some fields omitted for simplicity
                'host': 'mettel.velocloud.net',
                'enterpriseId': 1,
                'edgeState': 'OFFLINE',
                'edgeId': 3,
                'edgeSerialNumber': edge_2_serial,
                'edgeHASerialNumber': None,
                'edgeHAState': None,
                'edgeIsHAPrimary': None,
                'links': [
                    {
                        'interface': 'RAY',
                        'linkState': 'DISCONNECTED',
                    },
                ],
            },
        }
        edges = [
            edge_1_primary,
            edge_1_standby,
            edge_2,
        ]

        logger = Mock()
        ha_repository = Mock()

        outage_repository = OutageRepository(logger, ha_repository)
        outage_repository.is_ha_hard_down_outage = Mock(side_effect=[
            True,
            False,
            False,
        ])

        result = outage_repository.filter_edges_by_outage_type(edges, outage_type)

        expected = [
            edge_1_primary,
        ]
        assert result == expected

    def is_link_down_outage_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=False)
        result = outage_repository.is_link_down_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_link_down_outage(edge_status)
        assert result is False

    def is_hard_down_outage_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=False)
        result = outage_repository.is_hard_down_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_hard_down_outage(edge_status)
        assert result is False

    def is_HA_link_down_outage_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=False)
        result = outage_repository.is_ha_link_down_outage(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_ha_link_down_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_ha_link_down_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_ha_link_down_outage(edge_status)
        assert result is True

    def is_HA_soft_down_outage_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_ha_soft_down_outage(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC9999999',
            'edgeHASerialNumber': 'VC1234567',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_ha_soft_down_outage(edge_status)
        assert result is True

    def is_HA_hard_down_outage_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=False)
        result = outage_repository.is_ha_hard_down_outage(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        ha_repository.is_ha_enabled = Mock(return_value=True)
        result = outage_repository.is_ha_hard_down_outage(edge_status)
        assert result is True

    def is_edge_up_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        result = outage_repository.is_edge_up(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        result = outage_repository.is_edge_up(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        result = outage_repository.is_edge_up(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        result = outage_repository.is_edge_up(edge_status)
        assert result is True

    def get_outage_type_by_edge_status_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=True)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is Outages.LINK_DOWN

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=True)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is Outages.HARD_DOWN

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=False)
        outage_repository.is_ha_link_down_outage = Mock(return_value=True)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is Outages.HA_LINK_DOWN

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=False)
        outage_repository.is_ha_link_down_outage = Mock(return_value=False)
        outage_repository.is_ha_soft_down_outage = Mock(return_value=True)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is Outages.HA_SOFT_DOWN

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=False)
        outage_repository.is_ha_link_down_outage = Mock(return_value=False)
        outage_repository.is_ha_soft_down_outage = Mock(return_value=False)
        outage_repository.is_ha_hard_down_outage = Mock(return_value=True)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is Outages.HA_HARD_DOWN

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=False)
        outage_repository.is_ha_link_down_outage = Mock(return_value=False)
        outage_repository.is_ha_soft_down_outage = Mock(return_value=False)
        outage_repository.is_ha_hard_down_outage = Mock(return_value=False)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is None

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': False,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=False)
        outage_repository.is_ha_link_down_outage = Mock(return_value=False)
        outage_repository.is_ha_soft_down_outage = Mock(return_value=False)
        outage_repository.is_ha_hard_down_outage = Mock(return_value=False)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is None

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': False,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.is_link_down_outage = Mock(return_value=False)
        outage_repository.is_hard_down_outage = Mock(return_value=False)
        outage_repository.is_ha_link_down_outage = Mock(return_value=False)
        outage_repository.is_ha_soft_down_outage = Mock(return_value=False)
        outage_repository.is_ha_hard_down_outage = Mock(return_value=False)
        result = outage_repository.get_outage_type_by_edge_status(edge_status)
        assert result is None

    def should_document_outage_test(self):
        logger = Mock()
        ha_repository = Mock()
        outage_repository = OutageRepository(logger, ha_repository)

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.LINK_DOWN)
        result = outage_repository.should_document_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': None,
            'edgeHAState': None,
            'edgeIsHAPrimary': None,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HARD_DOWN)
        result = outage_repository.should_document_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': False,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HA_LINK_DOWN)
        ha_repository.is_ha_primary = Mock(return_value=False)
        result = outage_repository.should_document_outage(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'CONNECTED',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HA_LINK_DOWN)
        ha_repository.is_ha_primary = Mock(return_value=True)
        result = outage_repository.should_document_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HA_SOFT_DOWN)
        result = outage_repository.should_document_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'CONNECTED',
            'edgeIsHAPrimary': False,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'STABLE',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HA_SOFT_DOWN)
        result = outage_repository.should_document_outage(edge_status)
        assert result is True

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': False,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HA_HARD_DOWN)
        ha_repository.is_ha_primary = Mock(return_value=False)
        result = outage_repository.should_document_outage(edge_status)
        assert result is False

        edge_status = {
            # Some fields omitted for simplicity
            'host': 'mettel.velocloud.net',
            'enterpriseId': 1,
            'edgeState': 'OFFLINE',
            'edgeId': 3,
            'edgeSerialNumber': 'VC1234567',
            'edgeHASerialNumber': 'VC9999999',
            'edgeHAState': 'OFFLINE',
            'edgeIsHAPrimary': True,
            'links': [
                {
                    'interface': 'RAY',
                    'linkState': 'DISCONNECTED',
                },
            ],
        }
        outage_repository.get_outage_type_by_edge_status = Mock(return_value=Outages.HA_HARD_DOWN)
        ha_repository.is_ha_primary = Mock(return_value=True)
        result = outage_repository.should_document_outage(edge_status)
        assert result is True
