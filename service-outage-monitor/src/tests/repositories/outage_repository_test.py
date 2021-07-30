from unittest.mock import Mock

from application.repositories.outage_repository import OutageRepository


class TestOutageRepository:

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

        outage_utils = OutageRepository(logger=logger)

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

        outage_utils = OutageRepository(logger=logger)

        result_1 = outage_utils.is_any_link_disconnected(links_1)
        result_2 = outage_utils.is_any_link_disconnected(links_2)

        assert result_1 is True
        assert result_2 is False

    def is_faulty_edge_test(self):
        edge_state_1 = 'CONNECTED'
        edge_state_2 = 'OFFLINE'

        logger = Mock()

        outage_utils = OutageRepository(logger=logger)

        result = outage_utils.is_faulty_edge(edge_state_1)
        assert result is False

        result = outage_utils.is_faulty_edge(edge_state_2)
        assert result is True

    def is_faulty_link_test(self):
        link_state_1 = 'STABLE'
        link_state_2 = 'DISCONNECTED'

        logger = Mock()

        outage_utils = OutageRepository(logger=logger)

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

        outage_repository = OutageRepository(logger=logger)

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
        outage_utils = OutageRepository(logger=logger)
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
