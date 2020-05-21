from unittest.mock import Mock

from application.repositories.outage_repository import OutageRepository


class TestOutageRepository:

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

        outage_utils = OutageRepository(logger=logger)

        result = outage_utils.is_there_an_outage(edge_status_1)
        assert result is False

        result = outage_utils.is_there_an_outage(edge_status_2)
        assert result is True

        result = outage_utils.is_there_an_outage(edge_status_3)
        assert result is True

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

    def is_outage_ticket_auto_resolvable_test(self):
        text_identifier = ("#*Automation Engine*#\n"
                           "Auto-resolving detail for serial\n")

        note_value1 = f"{text_identifier}TimeStamp: 2021-01-02 10:18:16-05:00"
        note_value2 = f"{text_identifier}TimeStamp: 2020-01-02 10:18:16-05:00"
        note_value3 = f"{text_identifier}TimeStamp: 2022-01-02 10:18:16-05:00"

        note_value4 = ("#*Automation Engine*#\n"
                       "Just another kind of note\n")

        ticket_notes1 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
            },
            {
                "noteId": 41894043,
                "noteValue": note_value4,
            },
        ]

        ticket_notes2 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
            },
            {
                "noteId": 41894041,
                "noteValue": note_value2,
            },
            {
                "noteId": 41894042,
                "noteValue": note_value4,
            },
        ]

        ticket_notes3 = [
            {
                "noteId": 41894040,
                "noteValue": note_value1,
            },
            {
                "noteId": 41894041,
                "noteValue": note_value4,
            },
            {
                "noteId": 41894042,
                "noteValue": note_value2,
            },
            {
                "noteId": 41894043,
                "noteValue": note_value3,
            }
        ]

        logger = Mock()
        outage_utils = OutageRepository(logger=logger)
        autoresolve_limit = 3

        ticket_bool1 = outage_utils.is_outage_ticket_auto_resolvable(ticket_notes1, autoresolve_limit)
        assert ticket_bool1 is True

        ticket_bool2 = outage_utils.is_outage_ticket_auto_resolvable(ticket_notes2, autoresolve_limit)
        assert ticket_bool2 is True

        ticket_bool3 = outage_utils.is_outage_ticket_auto_resolvable(ticket_notes3, autoresolve_limit)
        assert ticket_bool3 is False
