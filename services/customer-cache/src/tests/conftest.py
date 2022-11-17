from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_customers import GetCustomers
from application.actions.refresh_cache import RefreshCache
from application.repositories.bruin_repository import BruinRepository
from application.repositories.email_repository import EmailRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.storage_repository import StorageRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig as config

# Scopes
# - function
# - module
# - session


@pytest.fixture(scope="function")
def mock_nats_client():
    nats_client = Mock()
    return nats_client


@pytest.fixture(scope="function")
def mock_redis():
    redis = Mock()
    return redis


@pytest.fixture(scope="function")
def mock_scheduler():
    scheduler = Mock()
    return scheduler


@pytest.fixture(scope="function")
def mock_storage_repository():
    storage_repository = Mock()
    return storage_repository


@pytest.fixture(scope="function")
def mock_velocloud_repository():
    velocloud_repository = Mock()
    return velocloud_repository


@pytest.fixture(scope="function")
def instance_notifications_repository(mock_nats_client):
    return NotificationsRepository(mock_nats_client, config)


@pytest.fixture(scope="function")
def instance_email_repository(mock_nats_client):
    return EmailRepository(mock_nats_client)


@pytest.fixture(scope="function")
def instance_velocloud_repository(mock_nats_client, instance_notifications_repository):
    return VelocloudRepository(config, mock_nats_client, instance_notifications_repository)


@pytest.fixture(scope="function")
def instance_bruin_repository(mock_nats_client, instance_notifications_repository):
    return BruinRepository(config, mock_nats_client, instance_notifications_repository)


@pytest.fixture(scope="function")
def instance_storage_repository(mock_redis):
    return StorageRepository(config, mock_redis)


@pytest.fixture(scope="function")
def instance_refresh_cache(
    mock_scheduler,
    mock_storage_repository,
    instance_bruin_repository,
    mock_velocloud_repository,
    instance_notifications_repository,
):
    return RefreshCache(
        config,
        mock_scheduler,
        mock_storage_repository,
        instance_bruin_repository,
        mock_velocloud_repository,
        instance_notifications_repository,
        instance_email_repository,
    )


@pytest.fixture(scope="function")
def instance_request_message():
    return {
        "request_id": "1111",
        "response_topic": "some.topic",
        "body": {"filter": {"mettel.velocloud.com": []}, "last_contact_filter": None},
    }


@pytest.fixture(scope="function")
def instance_request_message_without_topic():
    return {"request_id": "1111", "body": {"filter": {"mettel.velocloud.com": []}, "last_contact_filter": None}}


@pytest.fixture(scope="function")
def instance_response_message():
    return {"body": "Cache is still being built for host(s): mettel.velocloud.com", "status": 202}


@pytest.fixture(scope="function")
def instance_cache_edges():
    return [
        {
            "edge": {"host": "some host", "enterprise_id": 123, "edge_id": 321},
            "edge_name": "Big Boss",
            "last_contact": str(datetime.now()),
            "logical_ids": ["list of logical ids"],
            "serial_number": "VC01",
            "ha_serial_number": "VC011",
            "bruin_client_info": {"client_id": 30000, "client_name": "MetTel", "site_id": 12345},
            "site_details": {
                # Some fields omitted for simplicity
                "primaryContactName": "Test",
                "primaryContactPhone": "123-456-7890",
                "primaryContactEmail": "test@mail.com",
            },
        },
        {
            "edge": {"host": "some host", "enterprise_id": 1, "edge_id": 321},
            "edge_name": "Otacon",
            "last_contact": str(datetime.now()),
            "logical_ids": ["list of logical ids"],
            "serial_number": "VC02",
            "ha_serial_number": "VC022",
            "bruin_client_info": {"client_id": 30000, "client_name": "MetTel", "site_id": 12345},
            "site_details": {
                # Some fields omitted for simplicity
                "primaryContactName": "Test",
                "primaryContactPhone": "123-456-7890",
                "primaryContactEmail": "test@mail.com",
            },
        },
    ]


@pytest.fixture(scope="function")
def example_response_velo_host():
    return {"host": "metvco02.mettel.net", "enterpriseId": 123, "edgeId": 321}


@pytest.fixture(scope="function")
def instance_edges_refresh_cache():
    return [
        {
            "edge": {"host": "metvco02.mettel.net", "enterprise_id": 123, "edge_id": 321},
            "logical_ids": ["list of logical ids"],
            "serial_number": "VC01",
            "ha_serial_number": "VC011",
        },
        {
            "edge": {"host": "metvco04.mettel.net", "enterprise_id": 123, "edge_id": 321},
            "logical_ids": ["list of logical ids"],
            "serial_number": "VC02",
            "ha_serial_number": "VC022",
        },
    ]


@pytest.fixture(scope="function")
def instance_err_msg_refresh_cache():
    return {
        "request_id": "1111",
        "message": (
            "[customer-cache] Too many consecutive failures happened while trying to claim the list "
            "of edges from Velocloud"
        ),
    }


@pytest.fixture(scope="function")
def instance_velocloud_request():
    return {
        "request_id": "2222",
        "body": {
            "host": "mettel.velocloud.net",
        },
    }


@pytest.fixture(scope="function")
def instance_enterprise_velocloud_request():
    return {"request_id": "2222", "body": {"host": "mettel.velocloud.net", "enterprise_id": "123"}}


@pytest.fixture(scope="function")
def instance_get_configuration_request():
    return {
        "request_id": 1234,
        "body": {
            "host": "mettel.velocloud.net",
            "enterprise_id": 4,
            "edge_id": 12,
        },
    }


@pytest.fixture(scope="function")
def instance_velocloud_response():
    return {
        "request_id": "2222",
        "body": [
            {
                "host": "some-host",
                "enterpriseId": 1,
                "edgeId": 1,
                "edgeSerialNumber": 1,
                "edgeHASerialNumber": 2,
                "edgeLastContact": str(datetime.now() - timedelta(days=31)),
            },
            {
                "host": "some-host",
                "enterpriseId": 1,
                "edgeId": 2,
                "edgeSerialNumber": 1,
                "edgeHASerialNumber": 2,
                "edgeLastContact": str(datetime.now() - timedelta(days=30)),
            },
        ],
        "status": 200,
    }


@pytest.fixture(scope="function")
def instance_get_customer(instance_storage_repository, instance_cache_edges):
    instance_storage_repository.get_cache = Mock(return_value=instance_cache_edges)
    return GetCustomers(config, instance_storage_repository)


@pytest.fixture(scope="function")
def instance_cache_edges_with_last_contact(instance_cache_edges):
    instance_cache_edges[0]["last_contact"] = str(datetime.now() - timedelta(days=6))
    instance_cache_edges[1]["last_contact"] = str(datetime.now() - timedelta(days=8))
    return instance_cache_edges


@pytest.fixture(scope="function")
def instance_get_customer_with_last_contact(instance_storage_repository, instance_cache_edges_with_last_contact):
    instance_storage_repository.get_cache = Mock(return_value=instance_cache_edges_with_last_contact)
    return GetCustomers(config, instance_storage_repository)


@pytest.fixture(scope="function")
def instance_get_customer_with_empty_cache(instance_storage_repository):
    instance_storage_repository.get_cache = Mock(return_value=[])
    return GetCustomers(config, instance_storage_repository)


@pytest.fixture(scope="function")
def instance_velocloud_response():
    return {
        "request_id": "2222",
        "body": [
            {
                "enterpriseName": "Fake name|86937|",
                "enterpriseId": 1,
                "enterpriseProxyId": None,
                "enterpriseProxyName": None,
                "edgeName": "FakeEdgeName",
                "edgeState": "CONNECTED",
                "edgeSystemUpSince": "2020-09-14T05:07:40.000Z",
                "edgeServiceUpSince": "2020-09-14T05:08:22.000Z",
                "edgeLastContact": "2018-06-24T20:27:44.000Z",
                "edgeId": 1,
                "edgeSerialNumber": "VC1234567",
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
            },
            {
                "enterpriseName": "Fake name|86937|",
                "enterpriseId": 1,
                "enterpriseProxyId": None,
                "enterpriseProxyName": None,
                "edgeName": "FakeEdgeName",
                "edgeState": "CONNECTED",
                "edgeSystemUpSince": "2020-09-14T05:07:40.000Z",
                "edgeServiceUpSince": "2020-09-14T05:08:22.000Z",
                "edgeLastContact": "2018-06-24T20:27:44.000Z",
                "edgeId": 2,
                "edgeSerialNumber": "VC8901234",
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
            },
        ],
        "status": 200,
    }


@pytest.fixture(scope="function")
def instance_enterprise_edge_response():
    return {
        "request_id": "2222",
        "body": [
            {
                "id": 1,
                "enterpriseId": 1,
                "serialNumber": "VC1234567",
                "links": [
                    {
                        "id": 3216,
                        "edgeId": 1,
                        "edgeSerialNumber": "VC1234567",
                        "edgeState": "CONNECTED",
                        "logicalId": "82:b2:34:26:c6:b6:0000",
                        "interface": "GE5",
                    },
                    {
                        "id": 3062,
                        "edgeId": 1,
                        "edgeSerialNumber": "VC1234567",
                        "edgeState": "CONNECTED",
                        "logicalId": "82:b2:34:26:c6:b6:0000",
                        "interface": "GE6",
                    },
                ],
            },
            {
                "id": 2,
                "enterpriseId": 1,
                "serialNumber": "VC8901234",
                "links": [
                    {
                        "id": 3216,
                        "edgeId": 2,
                        "edgeSerialNumber": "VC8901234",
                        "logicalId": "82:b2:34:26:c6:b6:0000",
                        "interface": "GE5",
                    },
                    {
                        "id": 3062,
                        "edgeId": 2,
                        "edgeSerialNumber": "VC8901234",
                        "logicalId": "82:b2:34:26:c6:b6:0000",
                        "interface": "GE6",
                    },
                ],
            },
        ],
        "status": 200,
    }


@pytest.fixture(scope="function")
def instance_special_velocloud_response():
    return {
        "request_id": "2222",
        "body": [
            {
                "enterpriseName": "Fake name|86937|",
                "enterpriseId": 1,
                "enterpriseProxyId": None,
                "enterpriseProxyName": None,
                "edgeName": "FakeEdgeName",
                "edgeState": "NEVER_ACTIVATED",
                "edgeSystemUpSince": "0000-00-00 00:00:00",
                "edgeServiceUpSince": "0000-00-00 00:00:00",
                "edgeLastContact": "0000-00-00 00:00:00",
                "edgeId": 2,
                "edgeSerialNumber": "VC8901234",
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
            },
            {
                "enterpriseName": "Fake name|86937|",
                "enterpriseId": 1,
                "enterpriseProxyId": None,
                "enterpriseProxyName": None,
                "edgeName": None,
                "edgeState": None,
                "edgeSystemUpSince": None,
                "edgeServiceUpSince": None,
                "edgeLastContact": None,
                "edgeId": None,
                "edgeSerialNumber": None,
                "edgeHASerialNumber": None,
                "edgeModelNumber": None,
                "edgeLatitude": None,
                "edgeLongitude": None,
                "displayName": None,
                "isp": None,
                "interface": None,
                "internalId": None,
                "linkState": None,
                "linkLastActive": None,
                "linkVpnState": None,
                "linkId": None,
                "linkIpAddress": None,
                "host": "mettel.velocloud.net",
            },
            {
                "enterpriseName": "Fake name|86937|",
                "enterpriseId": 11888,
                "enterpriseProxyId": None,
                "enterpriseProxyName": None,
                "edgeName": None,
                "edgeState": None,
                "edgeSystemUpSince": None,
                "edgeServiceUpSince": None,
                "edgeLastContact": None,
                "edgeId": None,
                "edgeSerialNumber": None,
                "edgeHASerialNumber": None,
                "edgeModelNumber": None,
                "edgeLatitude": None,
                "edgeLongitude": None,
                "displayName": None,
                "isp": None,
                "interface": None,
                "internalId": None,
                "linkState": None,
                "linkLastActive": None,
                "linkVpnState": None,
                "linkId": None,
                "linkIpAddress": None,
                "host": "mettel.velocloud.net",
            },
        ],
        "status": 200,
    }


@pytest.fixture(scope="function")
def instance_config_response():
    return {
        "request_id": 1234,
        "body": [
            {
                "logicalId": "76:54:7d:99:b3:2e:0000",
                "internalId": "00000201-4c15-4e09-8e0e-a89a395a2aa4",
                "discovery": "AUTO_DISCOVERED",
                "mode": "PUBLIC",
                "type": "WIRED",
                "name": "69.141.202.71",
                "isp": None,
                "publicIpAddress": "69.141.202.71",
                "sourceIpAddress": None,
                "nextHopIpAddress": None,
                "customVlanId": False,
                "vlanId": 0,
                "virtualIpAddress": None,
                "dynamicBwAdjustmentEnabled": False,
                "bwMeasurement": "SLOW_START",
                "upstreamMbps": None,
                "downstreamMbps": None,
                "backupOnly": False,
                "udpHolePunching": False,
                "overheadBytes": 0,
                "MTU": 1500,
                "mplsNetwork": "",
                "dscpTag": "",
                "staticSlaEnabled": False,
                "classesofServiceEnabled": False,
                "encryptOverlay": True,
                "staticSLA": {"latencyMs": 0, "jitterMs": 0, "lossPct": 0},
                "classesOfService": {"classId": None, "classesOfService": []},
                "interfaces": ["SFP1"],
                "lastActive": 1565622307499,
            },
            {
                "logicalId": "90:6c:ac:bb:c9:8c:0000",
                "internalId": "00000001-4c15-4e09-8e0e-a89a395a2aa4",
                "discovery": "AUTO_DISCOVERED",
                "mode": "PUBLIC",
                "type": "WIRED",
                "name": "96.67.144.85",
                "isp": None,
                "publicIpAddress": "96.67.144.85",
                "sourceIpAddress": None,
                "nextHopIpAddress": None,
                "customVlanId": False,
                "vlanId": 0,
                "virtualIpAddress": None,
                "dynamicBwAdjustmentEnabled": False,
                "bwMeasurement": "SLOW_START",
                "upstreamMbps": None,
                "downstreamMbps": None,
                "backupOnly": False,
                "udpHolePunching": False,
                "overheadBytes": 0,
                "MTU": 1500,
                "mplsNetwork": "",
                "dscpTag": "",
                "staticSlaEnabled": False,
                "classesofServiceEnabled": False,
                "encryptOverlay": True,
                "staticSLA": {"latencyMs": 0, "jitterMs": 0, "lossPct": 0},
                "classesOfService": {"classId": None, "classesOfService": []},
                "interfaces": ["GE1"],
                "lastActive": 1580508612156,
            },
        ],
        "status": 200,
    }
