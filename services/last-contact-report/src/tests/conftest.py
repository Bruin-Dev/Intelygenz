from collections import OrderedDict
from datetime import datetime
from unittest.mock import Mock

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from shortuuid import uuid

from application.actions.alert import Alert
from application.repositories.email_repository import EmailRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.template_management import TemplateRenderer
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig

# Scopes
# - function
# - module
# - session


@pytest.fixture(scope="function")
def logger():
    logger = Mock()
    return logger


@pytest.fixture(scope="function")
def nats_client():
    nats_client = Mock()
    return nats_client


@pytest.fixture(scope="function")
def scheduler():
    return Mock(spec_set=AsyncIOScheduler)


@pytest.fixture(scope="function")
def notifications_repository(nats_client):
    return NotificationsRepository(nats_client, testconfig)


@pytest.fixture(scope="function")
def email_repository(nats_client):
    return EmailRepository(nats_client)


@pytest.fixture(scope="function")
def velocloud_repository(nats_client, logger, notifications_repository):
    return VelocloudRepository(nats_client, testconfig, notifications_repository)


@pytest.fixture(scope="function")
def alert(nats_client, logger, email_repository, scheduler):
    template_renderer = TemplateRenderer(testconfig.REPORT_CONFIG)
    return Alert(scheduler, testconfig, velocloud_repository, template_renderer, email_repository)


@pytest.fixture(scope="function")
def edge_link_host1():
    return {
        "enterpriseName": "Fake name|86937|",
        "enterpriseId": 2,
        "enterpriseProxyId": None,
        "enterpriseProxyName": None,
        "edgeName": "FakeEdgeName",
        "edgeState": "CONNECTED",
        "edgeSystemUpSince": "2020-09-14T05:07:40.000Z",
        "edgeServiceUpSince": "2020-09-14T05:08:22.000Z",
        "edgeLastContact": "2018-06-24T20:27:44.000Z",
        "edgeId": 4206,
        "edgeSerialNumber": "FK05200048223",
        "edgeHASerialNumber": None,
        "edgeModelNumber": "edge520",
        "edgeLatitude": None,
        "edgeLongitude": None,
        "displayName": "70.59.5.185",
        "isp": None,
        "interface": "GE1",
        "internalId": "00000001-ac48-47a0-81a7-80c8c320f486",
        "linkState": "STABLE",
        "linkLastActive": "2020-09-29T04:45:15.000Z",
        "linkVpnState": "STABLE",
        "linkId": 5293,
        "linkIpAddress": "0.0.0.0",
        "host": "mettel.velocloud.net",
    }


@pytest.fixture(scope="function")
def edge_link_host2():
    return {
        "enterpriseName": "Fake name|86937|",
        "enterpriseId": 2,
        "enterpriseProxyId": None,
        "enterpriseProxyName": None,
        "edgeName": "FakeEdgeName",
        "edgeState": "CONNECTED",
        "edgeSystemUpSince": "2020-09-14T05:07:40.000Z",
        "edgeServiceUpSince": "2020-09-14T05:08:22.000Z",
        "edgeLastContact": "2018-06-24T20:27:44.000Z",
        "edgeId": 4206,
        "edgeSerialNumber": "FK05200048223",
        "edgeHASerialNumber": None,
        "edgeModelNumber": "edge520",
        "edgeLatitude": None,
        "edgeLongitude": None,
        "displayName": "70.59.5.185",
        "isp": None,
        "interface": "GE1",
        "internalId": "00000001-ac48-47a0-81a7-80c8c320f486",
        "linkState": "STABLE",
        "linkLastActive": "2020-09-29T04:45:15.000Z",
        "linkVpnState": "STABLE",
        "linkId": 5293,
        "linkIpAddress": "0.0.0.0",
        "host": "metvco02.mettel.net",
    }


@pytest.fixture(scope="function")
def edge_link_host3():
    return {
        "enterpriseName": "Fake name|86937|",
        "enterpriseId": 2,
        "enterpriseProxyId": None,
        "enterpriseProxyName": None,
        "edgeName": "FakeEdgeName",
        "edgeState": "CONNECTED",
        "edgeSystemUpSince": "2020-09-14T05:07:40.000Z",
        "edgeServiceUpSince": "2020-09-14T05:08:22.000Z",
        "edgeLastContact": "2018-06-24T20:27:44.000Z",
        "edgeId": 4206,
        "edgeSerialNumber": "FK05200048223",
        "edgeHASerialNumber": None,
        "edgeModelNumber": "edge520",
        "edgeLatitude": None,
        "edgeLongitude": None,
        "displayName": "70.59.5.185",
        "isp": None,
        "interface": "GE1",
        "internalId": "00000001-ac48-47a0-81a7-80c8c320f486",
        "linkState": "STABLE",
        "linkLastActive": "2020-09-29T04:45:15.000Z",
        "linkVpnState": "STABLE",
        "linkId": 5293,
        "linkIpAddress": "0.0.0.0",
        "host": "metvco03.mettel.net",
    }


@pytest.fixture(scope="function")
def edge_link_list(edge_link_host1, edge_link_host2, edge_link_host3):
    return [edge_link_host1, edge_link_host1, edge_link_host2, edge_link_host3]


@pytest.fixture(scope="function")
def email_obj():
    email_html = "<html>html</html>"
    return {
        "request_id": uuid(),
        "body": {
            "email_data": {
                "subject": f'Last contact edges ({datetime.now().strftime("%Y-%m-%d")})',
                "recipient": testconfig.REPORT_CONFIG["recipient"],
                "text": "this is the accessible text for the email",
                "html": email_html,
                "images": [
                    {"name": "logo", "data": "LOGOBASE64"},
                    {"name": "header", "data": "HEADERBASE64"},
                ],
                "attachments": [{"name": "CSV", "data": "DATACSV"}],
            },
        },
    }


@pytest.fixture(scope="function")
def list_edge_alert():
    return [
        OrderedDict(
            [
                ("edge_name", "FakeEdgeName"),
                ("enterprise", "Fake name|86937|"),
                ("serial_number", "FK05200048223"),
                ("model number", "edge520"),
                ("last_contact", "2018-06-24T20:27:44.000Z"),
                ("months in SVC", 1),
                ("balance of the 36 months", 35),
                ("url", "https://mettel.velocloud.net/#!/operator/customer/2/monitor/edge/4206/"),
            ]
        ),
        OrderedDict(
            [
                ("edge_name", "FakeEdgeName"),
                ("enterprise", "Fake name|86937|"),
                ("serial_number", "FK05200048223"),
                ("model number", "edge520"),
                ("last_contact", "2018-06-24T20:27:44.000Z"),
                ("months in SVC", 1),
                ("balance of the 36 months", 35),
                ("url", "https://mettel.velocloud.net/#!/operator/customer/2/monitor/edge/4206/"),
            ]
        ),
        OrderedDict(
            [
                ("edge_name", "FakeEdgeName"),
                ("enterprise", "Fake name|86937|"),
                ("serial_number", "FK05200048223"),
                ("model number", "edge520"),
                ("last_contact", "2018-06-24T20:27:44.000Z"),
                ("months in SVC", 1),
                ("balance of the 36 months", 35),
                ("url", "https://metvco02.mettel.net/#!/operator/customer/2/monitor/edge/4206/"),
            ]
        ),
        OrderedDict(
            [
                ("edge_name", "FakeEdgeName"),
                ("enterprise", "Fake name|86937|"),
                ("serial_number", "FK05200048223"),
                ("model number", "edge520"),
                ("last_contact", "2018-06-24T20:27:44.000Z"),
                ("months in SVC", 1),
                ("balance of the 36 months", 35),
                ("url", "https://metvco03.mettel.net/#!/operator/customer/2/monitor/edge/4206/"),
            ]
        ),
    ]
