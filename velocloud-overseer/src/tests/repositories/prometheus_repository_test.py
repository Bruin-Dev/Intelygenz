import application
from prometheus_client import Gauge, REGISTRY
from application.repositories.prometheus_repository import PrometheusRepository
from config import testconfig as config
from unittest.mock import Mock


class TestPrometheusRepository:
    test_pro_repo = PrometheusRepository(config)

    def instance_test(self):
        assert self.test_pro_repo._config == config
        assert isinstance(self.test_pro_repo._edge_gauge, Gauge) is True

    def set_cycle_total_edges_test(self):
        sum = 123
        self.test_pro_repo.set_cycle_total_edges(sum)
        assert REGISTRY.get_sample_value('edges_processed') == 123

    def reset_counter_test(self):
        sum = 123
        self.test_pro_repo.set_cycle_total_edges(sum)
        self.test_pro_repo.reset_edges_counter()
        assert REGISTRY.get_sample_value('edges_processed') == 0

    def start_prometheus_metrics_server_test(self):
        mock_server = application.repositories.prometheus_repository.start_http_server = Mock()
        self.test_pro_repo.start_prometheus_metrics_server()
        assert mock_server.called is True
