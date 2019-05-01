import application
from prometheus_client import Gauge, REGISTRY
from application.repositories.prometheus_repository import PrometheusRepository
from config import testconfig as config
from unittest.mock import Mock


class TestPrometheusRepository:
    test_velocloud_repo = Mock()
    test_pro_repo = PrometheusRepository(config, test_velocloud_repo)

    def instance_test(self):

        assert self.test_pro_repo._config == config
        assert self.test_pro_repo._velocloud_repository == self.test_velocloud_repo
        assert isinstance(self.test_pro_repo._edge_gauge, Gauge) is True

    def inc_test(self):
        self.test_pro_repo._velocloud_repository.get_edge_count = Mock(return_value=123)
        self.test_pro_repo.inc()
        assert REGISTRY.get_sample_value('edges_processed') == 123

    def reset_counter_test(self):
        self.test_pro_repo._velocloud_repository.get_edge_count = Mock(return_value=123)
        self.test_pro_repo.inc()
        self.test_pro_repo.reset_counter()
        assert REGISTRY.get_sample_value('edges_processed') == 0

    def start_prometheus_metrics_server_test(self):
        mock_server = application.repositories.prometheus_repository.start_http_server = Mock()
        self.test_pro_repo.start_prometheus_metrics_server()
        assert mock_server.called is True
