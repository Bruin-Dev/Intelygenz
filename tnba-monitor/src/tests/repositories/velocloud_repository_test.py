from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import velocloud_repository as velocloud_repository_module
from application.repositories import nats_error_response
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, 'uuid', return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self, velocloud_repository, event_bus, logger, notifications_repository):
        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is testconfig
        assert velocloud_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_links_with_edge_info_default_rpc_timeout_test(self, velocloud_repository, make_rpc_request,
                                                                make_rpc_response, make_link_with_edge_info,
                                                                edge_1_connected, link_1_stable, link_2_stable):
        host = 'mettel.velocloud.net'

        request = make_rpc_request(request_id=uuid_, host=host)

        link_1_with_edge_info = make_link_with_edge_info(edge_info=edge_1_connected, link_info=link_1_stable)
        link_2_with_edge_info = make_link_with_edge_info(edge_info=edge_1_connected, link_info=link_2_stable)
        response = make_rpc_response(request_id=uuid_, body=[link_1_with_edge_info, link_2_with_edge_info], status=200)

        velocloud_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await velocloud_repository.get_links_with_edge_info(host)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.with.edge.info", request, timeout=30
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_rpc_request_failing_test(self, velocloud_repository, make_rpc_request):
        host = 'mettel.velocloud.net'
        request = make_rpc_request(request_id=uuid_, host=host)

        velocloud_repository._event_bus.rpc_request.side_effect = Exception
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await velocloud_repository.get_links_with_edge_info(host)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.with.edge.info", request, timeout=30
        )
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        velocloud_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_links_with_edge_info_with_rpc_request_returning_non_2xx_status_test(self, velocloud_repository,
                                                                                      make_rpc_request,
                                                                                      make_rpc_response):
        host = 'mettel.velocloud.net'

        request = make_rpc_request(request_id=uuid_, host=host)
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Velocloud',
            status=500,
        )

        velocloud_repository._event_bus.rpc_request.return_value = response
        velocloud_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await velocloud_repository.get_links_with_edge_info(host)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "get.links.with.edge.info", request, timeout=30
        )
        velocloud_repository._notifications_repository.send_slack_message.assert_awaited_once()
        velocloud_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_edges_for_tnba_monitoring_test(self, velocloud_repository, make_rpc_response,
                                                 make_link_with_edge_info, edge_1_connected, link_1_stable,
                                                 link_2_stable):
        hosts = testconfig.MONITOR_CONFIG["velo_filter"]

        link_1_with_edge_info = make_link_with_edge_info(edge_info=edge_1_connected, link_info=link_1_stable)
        link_2_with_edge_info = make_link_with_edge_info(edge_info=edge_1_connected, link_info=link_2_stable)
        links_with_edge_info = [
            link_1_with_edge_info,
            link_2_with_edge_info,
        ]
        response = make_rpc_response(request_id=uuid_, body=links_with_edge_info, status=200)

        velocloud_repository.get_links_with_edge_info.return_value = response

        await velocloud_repository.get_edges_for_tnba_monitoring()

        for host in hosts:
            velocloud_repository.get_links_with_edge_info.assert_awaited_once_with(velocloud_host=host)
        velocloud_repository.group_links_by_serial.assert_called_once_with(links_with_edge_info)

    def group_links_by_serial_test(self, velocloud_repository, make_link_with_edge_info, make_edge_with_links_info,
                                   edge_1_connected, link_1_stable, link_2_stable):
        link_1_with_edge_info = make_link_with_edge_info(edge_info=edge_1_connected, link_info=link_1_stable)
        link_2_with_edge_info = make_link_with_edge_info(edge_info=edge_1_connected, link_info=link_2_stable)
        links_with_edge_info = [
            link_1_with_edge_info,
            link_2_with_edge_info,
        ]

        result = velocloud_repository.group_links_by_serial(links_with_edge_info)

        expected = [
            make_edge_with_links_info(edge_info=edge_1_connected, links_info=[link_1_stable, link_2_stable]),
        ]
        assert result == expected
