from unittest.mock import Mock

import base64
from datetime import datetime
import pytest
from shortuuid import uuid
from config import testconfig
from collections import OrderedDict
from application.actions.alert import Alert
from application.repositories.velocloud_repository import VelocloudRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.template_management import TemplateRenderer


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def logger():
    logger = Mock()
    return logger


@pytest.fixture(scope='function')
def event_bus():
    event_bus = Mock()
    return event_bus


@pytest.fixture(scope='function')
def notifications_repository(event_bus):
    return NotificationsRepository(event_bus, testconfig)


@pytest.fixture(scope='function')
def velocloud_repository(event_bus, logger, notifications_repository):
    return VelocloudRepository(event_bus, logger, testconfig, notifications_repository)


@pytest.fixture(scope='function')
def alert(event_bus, logger, notifications_repository):
    scheduler = Mock()
    template_renderer = TemplateRenderer(testconfig.REPORT_CONFIG)
    return Alert(event_bus, scheduler, logger, testconfig, velocloud_repository, template_renderer,
                 notifications_repository)


@pytest.fixture(scope='function')
def edge_link_host1():
    return {
        'enterpriseName': 'Fake name|86937|',
        'enterpriseId': 2,
        'enterpriseProxyId': None,
        'enterpriseProxyName': None,
        'edgeName': 'FakeEdgeName',
        'edgeState': 'CONNECTED',
        'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
        'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
        'edgeLastContact': "2018-06-24T20:27:44.000Z",
        'edgeId': 4206,
        'edgeSerialNumber': 'FK05200048223',
        'edgeHASerialNumber': None,
        'edgeModelNumber': 'edge520',
        'edgeLatitude': None,
        'edgeLongitude': None,
        'displayName': '70.59.5.185',
        'isp': None, 'interface': 'GE1',
        'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
        'linkState': 'STABLE',
        'linkLastActive': '2020-09-29T04:45:15.000Z',
        'linkVpnState': 'STABLE',
        'linkId': 5293,
        'linkIpAddress': '0.0.0.0',
        'host': 'mettel.velocloud.net'
    }


@pytest.fixture(scope='function')
def edge_link_host2():
    return {
        'enterpriseName': 'Fake name|86937|',
        'enterpriseId': 2,
        'enterpriseProxyId': None,
        'enterpriseProxyName': None,
        'edgeName': 'FakeEdgeName',
        'edgeState': 'CONNECTED',
        'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
        'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
        'edgeLastContact': "2018-06-24T20:27:44.000Z",
        'edgeId': 4206,
        'edgeSerialNumber': 'FK05200048223',
        'edgeHASerialNumber': None,
        'edgeModelNumber': 'edge520',
        'edgeLatitude': None,
        'edgeLongitude': None,
        'displayName': '70.59.5.185',
        'isp': None, 'interface': 'GE1',
        'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
        'linkState': 'STABLE',
        'linkLastActive': '2020-09-29T04:45:15.000Z',
        'linkVpnState': 'STABLE',
        'linkId': 5293,
        'linkIpAddress': '0.0.0.0',
        'host': 'metvco02.mettel.net'
    }


@pytest.fixture(scope='function')
def edge_link_host3():
    return {
        'enterpriseName': 'Fake name|86937|',
        'enterpriseId': 2,
        'enterpriseProxyId': None,
        'enterpriseProxyName': None,
        'edgeName': 'FakeEdgeName',
        'edgeState': 'CONNECTED',
        'edgeSystemUpSince': '2020-09-14T05:07:40.000Z',
        'edgeServiceUpSince': '2020-09-14T05:08:22.000Z',
        'edgeLastContact': "2018-06-24T20:27:44.000Z",
        'edgeId': 4206,
        'edgeSerialNumber': 'FK05200048223',
        'edgeHASerialNumber': None,
        'edgeModelNumber': 'edge520',
        'edgeLatitude': None,
        'edgeLongitude': None,
        'displayName': '70.59.5.185',
        'isp': None, 'interface': 'GE1',
        'internalId': '00000001-ac48-47a0-81a7-80c8c320f486',
        'linkState': 'STABLE',
        'linkLastActive': '2020-09-29T04:45:15.000Z',
        'linkVpnState': 'STABLE',
        'linkId': 5293,
        'linkIpAddress': '0.0.0.0',
        'host': 'metvco03.mettel.net'
    }


@pytest.fixture(scope='function')
def edge_link_list(edge_link_host1, edge_link_host2, edge_link_host3):
    return [edge_link_host1, edge_link_host1, edge_link_host2, edge_link_host3]


@pytest.fixture(scope='function')
def email_obj():
    email_html = '<html>html</html>'
    return {
        'request_id': uuid(),
        'email_data': {
            'subject': f'Last contact edges ({datetime.now().strftime("%Y-%m-%d")})',
            'recipient': testconfig.REPORT_CONFIG["recipient"],
            'text': 'this is the accessible text for the email',
            'html': email_html,
            'images': [
                {
                    'name': 'logo',
                    'data': 'LOGOBASE64'
                },
                {
                    'name': 'header',
                    'data': 'HEADERBASE64'
                },
            ],
            'attachments': [
                {
                    'name': 'CSV',
                    'data': 'DATACSV'
                }
            ]
        }
    }


@pytest.fixture(scope='function')
def list_edge_alert():
    return [
        OrderedDict([
            ('edge_name',
             'FakeEdgeName'),
            ('enterprise',
             'Fake name|86937|'),
            ('serial_number',
             'FK05200048223'),
            ('model number',
             'edge520'),
            ('last_contact',
             '2018-06-24T20:27:44.000Z'),
            ('months in SVC',
             1),
            ('balance of the 36 months',
             35),
            ('url',
             'https://mettel.velocloud.net/#!/operator/customer/2/monitor/edge/4206/')
        ]),
        OrderedDict([
            ('edge_name',
             'FakeEdgeName'),
            ('enterprise',
             'Fake name|86937|'),
            ('serial_number',
             'FK05200048223'),
            ('model number',
             'edge520'),
            ('last_contact',
             '2018-06-24T20:27:44.000Z'),
            ('months in SVC',
             1),
            ('balance of the 36 months',
             35),
            ('url',
             'https://mettel.velocloud.net/#!/operator/customer/2/monitor/edge/4206/')
        ]),
        OrderedDict([
            ('edge_name',
             'FakeEdgeName'),
            ('enterprise',
             'Fake name|86937|'),
            ('serial_number',
             'FK05200048223'),
            ('model number',
             'edge520'),
            ('last_contact',
             '2018-06-24T20:27:44.000Z'),
            ('months in SVC',
             1),
            ('balance of the 36 months',
             35),
            ('url',
             'https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/4206/')
        ]),
        OrderedDict([
            ('edge_name',
             'FakeEdgeName'),
            ('enterprise',
             'Fake name|86937|'),
            ('serial_number',
             'FK05200048223'),
            ('model number',
             'edge520'),
            ('last_contact',
             '2018-06-24T20:27:44.000Z'),
            ('months in SVC',
             1),
            ('balance of the 36 months',
             35),
            ('url',
             'https://metvco03.mettel.net/#!/operator/customer/2/monitor/edge/4206/')
        ])
    ]
