from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories import nats_error_response
from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories.velocloud_repository import VelocloudRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)


class TestVelocloudRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig

        velocloud_repository = VelocloudRepository(config, logger, event_bus)

        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is config

    @pytest.mark.asyncio
    async def get_all_velo_edges_test(self, instance_velocloud_repository):
        edge_list = ["Edge list"]

        instance_velocloud_repository._get_all_edge_lists_parallel = CoroutineMock(return_value=edge_list)
        instance_velocloud_repository._get_all_serials_in_parallel = CoroutineMock()

        await instance_velocloud_repository.get_all_velo_edges()
        instance_velocloud_repository._get_all_edge_lists_parallel.assert_awaited_with(
            instance_velocloud_repository._config.REFRESH_CONFIG["velo_servers"])
        instance_velocloud_repository._get_all_serials_in_parallel.assert_awaited_with(edge_list)

    @pytest.mark.asyncio
    async def get_all_edge_lists_parallel_test(self, instance_velocloud_repository):
        edge_list_ok = {'body': ['test edge'], 'status': 200}
        edge_list_fail = {'body': 'failed', 'status': 400}

        instance_velocloud_repository.get_edges = CoroutineMock(side_effect=[edge_list_ok,
                                                                             edge_list_ok,
                                                                             edge_list_fail,
                                                                             edge_list_ok])

        full_edge_list = await instance_velocloud_repository._get_all_edge_lists_parallel(
            instance_velocloud_repository._config.REFRESH_CONFIG["velo_servers"])

        instance_velocloud_repository.get_edges.assert_awaited()

        assert full_edge_list == ['test edge', 'test edge', 'test edge']

    @pytest.mark.asyncio
    async def get_all_serials_in_parallel_test(self, instance_velocloud_repository):
        serial_number = "VCO1"
        last_contact = str(datetime.now())
        edge_id = {'host': 'some host', 'enterprise_id': 123, 'edge_id': 321}
        edge_status_1 = {'body': 'failed', 'status': 400}
        edge_status_2 = {'body': {'edge_id': edge_id, 'edge_info': {'edges': {'serialNumber': serial_number,
                                                                              'lastContact': last_contact}}},
                         'status': 200}
        edge_status_3 = {'body': {'edge_id': edge_id, 'edge_info': {'edges': {'lastContact': '0000-00-00 00:00:00'}}},
                         'status': 200}
        edge_status_4 = {'body': {'edge_id': edge_id, 'edge_info': {'edges': {'lastContact': last_contact}}},
                         'status': 200}
        edge_list = [edge_id, edge_id, edge_id, edge_id]

        instance_velocloud_repository.get_edge_status = CoroutineMock(side_effect=[edge_status_1,
                                                                                   edge_status_2,
                                                                                   edge_status_3,
                                                                                   edge_status_4
                                                                                   ])

        full_edge_serial = await instance_velocloud_repository._get_all_serials_in_parallel(edge_list)

        instance_velocloud_repository.get_edge_status.assert_awaited()

        assert full_edge_serial == [{'edge': edge_id, 'serial_number': serial_number, 'last_contact': last_contact}]

    @pytest.mark.asyncio
    async def get_edges_with_default_rpc_timeout_test(self, instance_velocloud_repository, instance_velocloud_request,
                                                      instance_velocloud_response):
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges({'mettel.velocloud.net': []})

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.list.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=300)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edges_with_custom_rpc_timeout_test(self, instance_velocloud_repository, instance_velocloud_request,
                                                     instance_velocloud_response):
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        rpc_timeout = 1000
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges({'mettel.velocloud.net': []},
                                                                   rpc_timeout=rpc_timeout)

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.list.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=rpc_timeout)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edges_with_no_filter_specified_test(self, instance_velocloud_repository, instance_velocloud_request,
                                                      instance_velocloud_response):
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        instance_velocloud_request['body']['filter'] = {}
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        with uuid_mock:
            result = await instance_velocloud_repository.get_edges()

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.list.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=300)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edges_with_rpc_request_failing_test(self, instance_velocloud_repository, instance_velocloud_request,
                                                      instance_velocloud_response):
        filter_ = {'mettel.velocloud.net': []}
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        instance_velocloud_request['body']['filter'] = filter_

        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        instance_velocloud_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_velocloud_repository.get_edges(filter_)

        instance_velocloud_repository._notify_error.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.list.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=300)
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_edges_with_rpc_request_returning_non_2xx_status_test(self, instance_velocloud_repository,
                                                                       instance_velocloud_request,
                                                                       instance_velocloud_response):
        filter_ = {'mettel.velocloud.net': []}
        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_response['request_id'] = uuid_
        instance_velocloud_response['body'] = 'Got internal error from Velocloud'
        instance_velocloud_response['status'] = 500
        instance_velocloud_request['body']['filter'] = filter_

        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        instance_velocloud_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_velocloud_repository.get_edges(filter_)

        instance_velocloud_repository._notify_error.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.list.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=300)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edge_status_test(self, instance_velocloud_repository, instance_velocloud_request,
                                   instance_velocloud_response):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_request['body'] = edge_full_id
        instance_velocloud_response['request_id'] = uuid_
        instance_velocloud_response['body'] = {
                                                  'edge_id': edge_full_id,
                                                  'edge_info': {
                                                      'edges': {'edgeState': 'OFFLINE', 'serialNumber': 'VC1234567'},
                                                      'links': [
                                                          {'linkId': 1234,
                                                           'link': {'state': 'DISCONNECTED', 'interface': 'GE1'}},
                                                          {'linkId': 5678,
                                                           'link': {'state': 'STABLE', 'interface': 'GE2'}},
                                                      ],
                                                      'enterprise_name': 'EVIL-CORP|12345|',
                                                  }
                                              },
        instance_velocloud_response['status'] = 200

        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)

        with uuid_mock:
            result = await instance_velocloud_repository.get_edge_status(edge_full_id)

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.status.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=120)
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def get_edge_status_with_rpc_request_failing_test(self, instance_velocloud_repository,
                                                            instance_velocloud_request):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_request['body'] = edge_full_id
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)
        instance_velocloud_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_velocloud_repository.get_edge_status(edge_full_id)

        instance_velocloud_repository._notify_error.assert_awaited_once()
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.status.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=120)
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_edge_status_with_rpc_request_returning_non_2xx_status_test(self, instance_velocloud_repository,
                                                                             instance_velocloud_response,
                                                                             instance_velocloud_request):
        edge_full_id = {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1}

        instance_velocloud_request['request_id'] = uuid_
        instance_velocloud_request['body'] = edge_full_id
        instance_velocloud_response['body'] = 'Got internal error from Velocloud',
        instance_velocloud_response['status'] = 500
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=instance_velocloud_response)
        instance_velocloud_repository._notify_error = CoroutineMock()

        with uuid_mock:
            result = await instance_velocloud_repository.get_edge_status(edge_full_id)

        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("edge.status.request",
                                                                                      instance_velocloud_request,
                                                                                      timeout=120)
        instance_velocloud_repository._notify_error.assert_awaited_once()
        assert result == instance_velocloud_response

    @pytest.mark.asyncio
    async def notify_error_test(self, instance_velocloud_repository):
        instance_velocloud_repository._event_bus.rpc_request = CoroutineMock()
        error_dict = {'request_id': uuid_,
                      'message': 'Failed'}
        with uuid_mock:
            await instance_velocloud_repository._notify_error('Failed')
        instance_velocloud_repository._event_bus.rpc_request.assert_awaited_once_with("notification.slack.request",
                                                                                      error_dict,
                                                                                      timeout=10)
