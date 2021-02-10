from unittest.mock import Mock

import pytest

from application.actions.tnba_monitor import TNBAMonitor
from config import testconfig as config


@pytest.fixture(scope='package')
def logger():
    return Mock()


@pytest.fixture(scope='package')
def event_bus():
    return Mock()


@pytest.fixture(scope='function')
def scheduler():
    return Mock()


@pytest.fixture(scope='package')
def t7_repository():
    return Mock()


@pytest.fixture(scope='package')
def ticket_repository():
    return Mock()


@pytest.fixture(scope='package')
def bruin_repository():
    return Mock()


@pytest.fixture(scope='package')
def velocloud_repository():
    return Mock()


@pytest.fixture(scope='package')
def prediction_repository():
    return Mock()


@pytest.fixture(scope='package')
def notifications_repository():
    return Mock()


@pytest.fixture(scope='package')
def utils_repository():
    return Mock()


@pytest.fixture(scope='package')
def customer_cache_repository():
    return Mock()


@pytest.fixture(scope='function')
def tnba_monitor(logger, event_bus, scheduler, t7_repository, ticket_repository,
                 customer_cache_repository, bruin_repository, velocloud_repository,
                 prediction_repository, notifications_repository, utils_repository):
    return TNBAMonitor(event_bus, logger, scheduler, config, t7_repository, ticket_repository,
                       customer_cache_repository, bruin_repository, velocloud_repository,
                       prediction_repository, notifications_repository, utils_repository)


@pytest.fixture(scope='package')
def make_structure_call():
    def _make_structure_call(request_id, topic, body):
        return {'request_id': request_id, 'response_topic': topic, 'body': body}

    return _make_structure_call


@pytest.fixture(scope='package')
def make_structure_response():
    def _make_structure_response(status, body):
        return {'status': status, 'body': body}

    return _make_structure_response


@pytest.fixture(scope='package')
def make_edge_id():
    def _make_edge_id(edges_host, edge_enterprise_id, edge_id):
        return {'host': edges_host, 'enterprise_id': edge_enterprise_id, 'edge_id': edge_id}

    return _make_edge_id


@pytest.fixture(scope='package')
def make_ticket_note_for_bruin():
    def _make_ticket_note_for_bruin(note_id=41894040,
                                    note_value=f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
                                    created_date="2020-02-24T10:07:13.503-05:00", service_number='VC1234567'):
        return {'noteId': note_id, 'noteValue': note_value, 'createdDate': created_date,
                'serviceNumber': service_number}

    return _make_ticket_note_for_bruin


@pytest.fixture(scope='package')
def make_tnba_note():
    def _make_tnba_note(ticket_id, text, detail_id, service_number):
        return {
            'ticket_id': ticket_id,
            'text': text,
            'detail_id': detail_id,
            'service_number': service_number,
        }

    return _make_tnba_note


@pytest.fixture(scope='package')
def make_payload_note():
    def _make_payload_note(text, detail_id, service_number):
        return {
            'text': text,
            'detail_id': detail_id,
            'service_number': service_number,
        }

    return _make_payload_note


@pytest.fixture(scope='package')
def make_cache_info():
    def _make_cache_info(edge_id, edge_serial, bruin_client_id, client_name):
        return {
            'edge': edge_id,
            'serial_number': edge_serial,
            'last_contact': '2020-08-27T15:25:42.000',
            'bruin_client_info': {
                'client_id': bruin_client_id,
                'client_name': client_name,
            }
        }

    return _make_cache_info


@pytest.fixture(scope='package')
def make_edge_status():
    def _make_edge_status(edges_host, edge_enterprise_id, edge_id, edge_serial_number):
        return {'host': edges_host, 'enterpriseId': edge_enterprise_id, 'edgeId': edge_id,
                'edgeSerialNumber': edge_serial_number}

    return _make_edge_status


@pytest.fixture(scope='package')
def make_edge_status():
    def _make_edge_status(edge_state='DISCONECTED', links=None, edges_host='some-host', edge_enterprise_id=1, edge_id=1,
                          edge_serial_number='VC1234567'):
        return {
            'host': edges_host,
            'enterpriseName': 'Militaires Sans Frontières',
            'enterpriseId': edge_enterprise_id,
            'enterpriseProxyId': None,
            'enterpriseProxyName': None,
            'edgeName': 'Big Boss',
            'edgeState': edge_state,
            'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
            'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
            'edgeLastContact': '2020-09-29T04:48:55.000Z',
            'edgeId': edge_id,
            'edgeSerialNumber': edge_serial_number,
            'edgeHASerialNumber': None,
            'edgeModelNumber': 'edge520',
            'edgeLatitude': None,
            'edgeLongitude': None,
            'displayName': '70.59.5.185',
            'isp': None,
            'links': links
        }

    return _make_edge_status


@pytest.fixture(scope='package')
def make_link():
    def _make_link(link_state):
        return {
            'interface': 'RAY',
            'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
            'linkState': link_state,
            'linkLastActive': '2020-09-29T04:45:15.000Z',
            'linkVpnState': 'STABLE',
            'linkId': 5293,
            'linkIpAddress': '70.59.5.185',
        }

    return _make_link


@pytest.fixture(scope='package')
def make_detail_object():
    def _make_detail_object(ticket_id, ticket_topic, ticket_creator, ticket_detail, ticket_notes,
                            ticket_detail_predictions, ticket_creation_date="1/03/2021 10:08:13 AM"):
        return {
            'ticket_id': ticket_id,
            'ticket_creation_date': ticket_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_detail': ticket_detail,
            'ticket_notes': ticket_notes,
            'ticket_detail_predictions': ticket_detail_predictions
        }

    return _make_detail_object


@pytest.fixture(scope='package')
def make_ticket_detail():
    def _make_ticket_detail(detail_id, detail_value):
        return {
            "detailID": detail_id,
            "detailValue": detail_value,
        }
    return _make_ticket_detail


@pytest.fixture(scope='package')
def make_ticket_details_bruin():
    def _make_ticket_details_bruin(ticket_id, ticket_creation_date, ticket_topic, ticket_creator, ticket_details,
                                   ticket_notes):
        return {
            'ticket_id': ticket_id,
            'ticket_creation_date': ticket_creation_date,
            'ticket_topic': ticket_topic,
            'ticket_creator': ticket_creator,
            'ticket_details': ticket_details,
            'ticket_notes': ticket_notes
        }

    return _make_ticket_details_bruin


@pytest.fixture(scope='package')
def make_prediction():
    def _make_prediction(name='Repair Completed', probability=0.9484384655952454):
        return {
            'name': name,
            'probability': probability
        }

    return _make_prediction


@pytest.fixture(scope='package')
def make_next_results():
    def _make_next_results():
        return {
            "currentTaskId": 10683187,
            "currentTaskKey": "344",
            "currentTaskName": "Holmdel NOC Investigate ",
            "nextResults": [
                {
                    "resultTypeId": 620,
                    "resultName": "Repair Completed",
                    "notes": [
                        {
                            "noteType": "Notes",
                            "noteDescription": "Notes",
                            "availableValueOptions": None,
                            "defaultValue": None,
                            "required": False,
                        }
                    ]
                }
            ],
        }

    return _make_next_results


@pytest.fixture(scope='package')
def customer_cache_1(make_edge_id, make_cache_info):
    bruin_client_1_id = 12345
    bruin_client_2_id = 67890
    edge_1_serial = 'VC1234567'
    edge_2_serial = 'VC7654321'
    edge_3_serial = 'VC1111111'

    return [
        make_cache_info(edge_id=make_edge_id(edges_host='some-host', edge_enterprise_id=1, edge_id=1),
                        edge_serial=edge_1_serial, bruin_client_id=bruin_client_1_id, client_name='Aperture Science'),
        make_cache_info(edge_id=make_edge_id(edges_host='some-host', edge_enterprise_id=1, edge_id=2),
                        edge_serial=edge_2_serial, bruin_client_id=bruin_client_2_id, client_name='Sarif Industries'),
        make_cache_info(edge_id=make_edge_id(edges_host='some-host', edge_enterprise_id=1, edge_id=3),
                        edge_serial=edge_3_serial, bruin_client_id=bruin_client_2_id, client_name='Sarif Industries'),
    ]


@pytest.fixture(scope='package')
def customer_cache_by_serial_1(make_edge_id, make_cache_info):
    bruin_client_1_id = 12345
    bruin_client_2_id = 67890
    edge_1_serial = 'VC1234567'
    edge_2_serial = 'VC7654321'
    edge_3_serial = 'VC1111111'

    return {
        edge_1_serial: make_cache_info(edge_id=make_edge_id(edges_host='some-host', edge_enterprise_id=1, edge_id=1),
                                       edge_serial=edge_1_serial, bruin_client_id=bruin_client_1_id,
                                       client_name='Aperture Science'),
        edge_2_serial: make_cache_info(edge_id=make_edge_id(edges_host='some-host', edge_enterprise_id=1, edge_id=2),
                                       edge_serial=edge_2_serial, bruin_client_id=bruin_client_2_id,
                                       client_name='Sarif Industries'),
        edge_3_serial: make_cache_info(edge_id=make_edge_id(edges_host='some-host', edge_enterprise_id=1, edge_id=3),
                                       edge_serial=edge_3_serial, bruin_client_id=bruin_client_2_id,
                                       client_name='Sarif Industries'),
    }


@pytest.fixture(scope='package')
def edge_status_1(make_edge_id, make_edge_status):
    edge_1_serial = 'VC1234567'
    edge_2_serial = 'VC7654321'
    edge_3_serial = 'VC1111111'
    host = 'some-host'
    return [
        make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=1, edge_serial_number=edge_1_serial),
        make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=2, edge_serial_number=edge_2_serial),
        make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=3, edge_serial_number=edge_3_serial),
    ]


@pytest.fixture(scope='package')
def edge_status_2(make_edge_id, make_edge_status, edge_status_1):
    edge_1_serial = 'VC7654321'
    edge_2_serial = 'VC1111111'
    edge_3_serial = 'VC2222222'
    host = 'some-host'
    return [
        make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=1, edge_serial_number=edge_1_serial),
        make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=2, edge_serial_number=edge_2_serial),
        make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=3, edge_serial_number=edge_3_serial),
    ]


@pytest.fixture(scope='package')
def edge_status_by_serial_1(make_edge_id, make_edge_status):
    edge_1_serial = 'VC1234567'
    edge_2_serial = 'VC7654321'
    edge_3_serial = 'VC1111111'
    host = 'some-host'
    return {
        edge_1_serial: make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=1,
                                        edge_serial_number=edge_1_serial),
        edge_2_serial: make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=2,
                                        edge_serial_number=edge_2_serial),
        edge_3_serial: make_edge_status(edges_host=host, edge_enterprise_id=1, edge_id=3,
                                        edge_serial_number=edge_3_serial),
    }
