import pytest
from shortuuid import uuid
from unittest.mock import Mock
from unittest.mock import patch
from asynctest import CoroutineMock
from config import testconfig
from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories.velocloud_repository import VelocloudRepository

from unittest.mock import call

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)


class TestVelocloudRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, testconfig, notifications_repository)
        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is testconfig
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_edges_links_by_host_test(self, velocloud_repository, edge_link_host1):
        request_id = uuid()
        host = 'mettel.velocloud.net'

        edge_request = {"request_id": request_id, "body": [edge_link_host1], 'status': 200}
        velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=edge_request)
        response = await velocloud_repository.get_edges_links_by_host(host)
        assert response['body'] == [edge_link_host1]
        assert response['status'] == 200

    @pytest.mark.asyncio
    async def get_edges_links_by_host_400_test(self, velocloud_repository):
        request_id = uuid()
        host = 'mettel.velocloud.net'
        response_status = 400
        response_body = []
        error_msg = (
            f'Error while retrieving edges links in DEV '
            f'environment: Error {response_status} - {response_body}'
        )
        edge_request = {"request_id": request_id, "body": response_body, 'status': response_status}
        velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=edge_request)

        velocloud_repository._notify_error = CoroutineMock(side_effect=[None])
        response = await velocloud_repository.get_edges_links_by_host(host)
        velocloud_repository._notify_error.assert_has_awaits([
            call(error_msg)
        ])
        assert response['body'] == []
        assert response['status'] == 400

    @pytest.mark.asyncio
    async def get_edges_links_by_host_exception_test(self, velocloud_repository):
        exception_msg = 'test exception'
        host = 'mettel.velocloud.net'
        error_msg = f'An error occurred when requesting edge list from {host} -> {exception_msg}'
        velocloud_repository._notify_error = CoroutineMock(side_effect=[None])
        velocloud_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception(exception_msg))
        response = await velocloud_repository.get_edges_links_by_host(host)
        velocloud_repository._notify_error.assert_has_awaits([
            call(error_msg)
        ])
        assert response['body'] is None
        assert response['status'] == 503

    @pytest.mark.asyncio
    async def get_all_edges_links_test(self, velocloud_repository, edge_link_list):
        host1 = 'mettel.velocloud.net'
        host2 = 'metvco02.mettel.net'
        host3 = 'metvco03.mettel.net'
        host4 = 'metvco04.mettel.net'
        response_get_links1 = {
            'status': 200,
            'body': [edge_link_list[0], edge_link_list[1]]
        }
        response_get_links2 = {
            'status': 200,
            'body': [edge_link_list[2]]
        }
        response_get_links3 = {
            'status': 200,
            'body': [edge_link_list[3]]
        }
        response_get_links4 = {
            'status': 200,
            'body': [edge_link_list[3]]
        }
        velocloud_repository.get_edges_links_by_host = CoroutineMock(
            side_effect=[response_get_links1, response_get_links2, response_get_links3, response_get_links4])
        response = await velocloud_repository.get_all_edges_links()
        velocloud_repository.get_edges_links_by_host.assert_has_awaits([
            call(host=host1),
            call(host=host2),
            call(host=host3),
            call(host=host4)
        ])
        assert response['status'] == 200
        assert response['body'] == [edge_link_list[0], edge_link_list[1], edge_link_list[2], edge_link_list[3],
                                    edge_link_list[3]]

    @pytest.mark.asyncio
    async def get_all_edges_links_400_test(self, velocloud_repository, edge_link_list):
        host1 = 'mettel.velocloud.net'
        host2 = 'metvco02.mettel.net'
        host3 = 'metvco03.mettel.net'
        host4 = 'metvco04.mettel.net'
        response_get_links1 = {
            'status': 200,
            'body': [edge_link_list[0], edge_link_list[1]]
        }
        response_get_links2 = {
            'status': 200,
            'body': [edge_link_list[2]]
        }
        response_get_links3 = {
            'status': 400,
            'body': [edge_link_list[3]]
        }
        response_get_links4 = {
            'status': 400,
            'body': [edge_link_list[3]]
        }
        velocloud_repository.get_edges_links_by_host = CoroutineMock(
            side_effect=[response_get_links1, response_get_links2, response_get_links3, response_get_links4])
        response = await velocloud_repository.get_all_edges_links()
        velocloud_repository.get_edges_links_by_host.assert_has_awaits([
            call(host=host1),
            call(host=host2),
            call(host=host3),
            call(host=host4)
        ])
        assert response['status'] == 200
        assert response['body'] == [edge_link_list[0], edge_link_list[1], edge_link_list[2]]

    @pytest.mark.asyncio
    async def get_edges_test(self, velocloud_repository, edge_link_list):
        velocloud_repository.get_all_edges_links = CoroutineMock(
            return_value={'body': edge_link_list})
        edge_list = await velocloud_repository.get_edges()
        assert len(edge_list) == 1

    @pytest.mark.asyncio
    async def get_edges_bad_id_test(self, velocloud_repository, edge_link_list):
        edge_link_list[0]['edgeId'] = None
        edge_link_list[1]['edgeId'] = None
        edge_link_list[2]['edgeId'] = None
        edge_link_list[3]['edgeId'] = None
        velocloud_repository.get_all_edges_links = CoroutineMock(
            return_value={'body': edge_link_list})
        edge_list = await velocloud_repository.get_edges()
        assert len(edge_list) == 0

    @pytest.mark.asyncio
    async def notify_error_test(self, velocloud_repository, ):
        slack_message = 'Error last contact notify'
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock(
            return_value=None)
        with uuid_mock:
            await velocloud_repository._notify_error(slack_message)
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once_with(slack_message)
