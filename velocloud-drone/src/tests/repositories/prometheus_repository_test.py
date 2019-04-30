import application
from prometheus_client import Gauge, Counter, REGISTRY, start_http_server
from application.repositories.prometheus_repository import PrometheusRepository
from config import testconfig as config
from unittest.mock import Mock, MagicMock
import asyncio
import pytest


class TestPrometheusRepository:
    test_pro_repo = PrometheusRepository(config)

    def instance_test(self):
        assert self.test_pro_repo._config == config
        assert isinstance(self.test_pro_repo._edge_status_gauge, Gauge) is True
        assert isinstance(self.test_pro_repo._link_status_gauge, Gauge) is True
        assert isinstance(self.test_pro_repo._edge_status_counter, Counter) is True
        assert isinstance(self.test_pro_repo._link_status_counter, Counter) is True

    def inc_test(self):
        test_enterprise_id = 1
        test_enterprise_name = 'Test'
        test_edge_state = 'Edge_OK'
        test_obj = MagicMock(_link=Mock(_state='OK'))
        test_link_status = [test_obj]
        self.test_pro_repo.inc(test_enterprise_id, test_enterprise_name, test_edge_state, test_link_status)
        self.test_pro_repo.inc(test_enterprise_id, test_enterprise_name, test_edge_state, test_link_status)
        assert REGISTRY.get_sample_value('edge_state_gauge', labels={'enterprise_id': str(test_enterprise_id),
                                                                     'enterprise_name': test_enterprise_name,
                                                                     'state': test_edge_state}) == 2
        assert REGISTRY.get_sample_value('edge_state_total', labels={'enterprise_id': str(test_enterprise_id),
                                                                     'enterprise_name': test_enterprise_name,
                                                                     'state': test_edge_state}) == 2

        assert REGISTRY.get_sample_value('link_state_gauge', labels={'enterprise_id': str(test_enterprise_id),
                                                                     'enterprise_name': test_enterprise_name,
                                                                     'state': 'OK'}) == 2
        assert REGISTRY.get_sample_value('link_state_total', labels={'enterprise_id': str(test_enterprise_id),
                                                                     'enterprise_name': test_enterprise_name,
                                                                     'state': 'OK'}) == 2

    @pytest.mark.asyncio
    async def reset_counter_test(self):
        test_enterprise_id = 1
        test_enterprise_name = 'Test'
        test_edge_state = 'Edge_OK'
        test_obj = MagicMock(_link=Mock(_state='OK'))
        test_link_status = [test_obj]
        self.test_pro_repo.inc(test_enterprise_id, test_enterprise_name, test_edge_state, test_link_status)
        self.test_pro_repo.inc(test_enterprise_id, test_enterprise_name, test_edge_state, test_link_status)
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self.test_pro_repo.reset_counter(), loop=loop)
        await asyncio.sleep(1.5)
        task.cancel()
        loop.stop()
        assert REGISTRY.get_sample_value('edge_state_gauge', labels={'enterprise_id': str(test_enterprise_id),
                                                                     'enterprise_name': test_enterprise_name,
                                                                     'state': test_edge_state}) is None
        assert REGISTRY.get_sample_value('edge_state_gauge', labels={'enterprise_id': str(test_enterprise_id),
                                                                     'enterprise_name': test_enterprise_name,
                                                                     'state': 'OK'}) is None

    def start_server_test(self):
        mock_server = application.repositories.prometheus_repository.start_http_server = Mock()
        self.test_pro_repo.start_server()
        assert mock_server.called is True
