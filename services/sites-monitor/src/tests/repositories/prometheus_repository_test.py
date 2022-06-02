import asyncio
from unittest.mock import MagicMock, Mock

import application
import pytest
from application.repositories.prometheus_repository import PrometheusRepository
from config import testconfig as config
from prometheus_client import REGISTRY, Counter, Gauge


class TestPrometheusRepository:
    test_pro_repo = PrometheusRepository(config)

    def instance_test(self):
        assert self.test_pro_repo._config == config
        assert isinstance(self.test_pro_repo._edge_gauge, Gauge) is True
        assert isinstance(self.test_pro_repo._edge_status_gauge, Gauge) is True
        assert isinstance(self.test_pro_repo._link_status_gauge, Gauge) is True

    def set_cycle_total_edges_test(self):
        sum = 123
        self.test_pro_repo.set_cycle_total_edges(sum)
        assert REGISTRY.get_sample_value("edges_processed") == 123

    def reset_edge_counter_test(self):
        sum = 123
        self.test_pro_repo.set_cycle_total_edges(sum)
        self.test_pro_repo.reset_edges_counter()
        assert REGISTRY.get_sample_value("edges_processed") == 0

    def inc_test(self):
        test_enterprise_name = "Test"
        test_edge_state = "Edge_OK"
        test_edge_name = "Test Edge Name"
        test_link_status = [{"linkState": "OK"}]
        test_edge = {
            "edgeState": test_edge_state,
            "edgeName": test_edge_name,
            "enterpriseName": test_enterprise_name,
            "links": test_link_status,
        }
        self.test_pro_repo.inc(test_edge)
        self.test_pro_repo.inc(test_edge)
        assert (
            REGISTRY.get_sample_value(
                "edge_state_gauge",
                labels={"enterprise_name": test_enterprise_name, "state": test_edge_state, "name": test_edge_name},
            )
            == 2
        )
        assert (
            REGISTRY.get_sample_value(
                "link_state_gauge", labels={"enterprise_name": test_enterprise_name, "state": "OK"}
            )
            == 2
        )

    def dec_test(self):
        test_enterprise_name = "Test"
        test_edge_state = "Edge_OK"
        test_edge_name = "Test Edge Name"
        test_link_status = [{"linkState": "OK"}]
        test_edge = {
            "edgeState": test_edge_state,
            "edgeName": test_edge_name,
            "enterpriseName": test_enterprise_name,
            "links": test_link_status,
        }
        self.test_pro_repo.reset_counter()
        self.test_pro_repo.inc(test_edge)
        self.test_pro_repo.inc(test_edge)
        self.test_pro_repo.dec(test_edge)
        assert (
            REGISTRY.get_sample_value(
                "edge_state_gauge",
                labels={"enterprise_name": test_enterprise_name, "state": test_edge_state, "name": test_edge_name},
            )
            == 1
        )
        assert (
            REGISTRY.get_sample_value(
                "link_state_gauge", labels={"enterprise_name": test_enterprise_name, "state": "OK"}
            )
            == 1
        )

    def update_edge_test(self):
        test_enterprise_name = "Test"
        test_edge_state = "Edge_OK"
        test_edge_name = "Test Edge Name"
        test_link_status = [{"linkState": "OK"}]
        test_edge = {
            "edgeState": test_edge_state,
            "edgeName": test_edge_name,
            "enterpriseName": test_enterprise_name,
            "links": test_link_status,
        }
        cache_test_enterprise_name = "Test"
        cache_edge_state = "Edge_KO"
        cache_edge_name = "Cached Test Edge Name"
        cache_link_status = [{"linkState": "KO"}]
        cache_edge = {
            "edgeState": cache_edge_state,
            "edgeName": cache_edge_name,
            "enterpriseName": cache_test_enterprise_name,
            "links": cache_link_status,
        }
        self.test_pro_repo.reset_counter()
        self.test_pro_repo.inc(cache_edge)
        self.test_pro_repo.update_edge(test_edge, cache_edge)

        assert (
            REGISTRY.get_sample_value(
                "edge_state_gauge",
                labels={"enterprise_name": test_enterprise_name, "state": test_edge_state, "name": test_edge_name},
            )
            == 1
        )
        assert (
            REGISTRY.get_sample_value(
                "edge_state_gauge",
                labels={
                    "enterprise_name": cache_test_enterprise_name,
                    "state": cache_edge_state,
                    "name": cache_edge_name,
                },
            )
            == 0
        )

    def update_link_test(self):
        test_enterprise_name = "Test"
        test_edge_state = "Edge_OK"
        test_edge_name = "Test Edge Name"
        test_link_status = [{"linkState": "OK"}]
        test_edge = {
            "edgeState": test_edge_state,
            "edgeName": test_edge_name,
            "enterpriseName": test_enterprise_name,
            "links": test_link_status,
        }
        cache_test_enterprise_name = "Test"
        cache_edge_state = "Edge_OK"
        cache_edge_name = "Cached Test Edge Name"
        cache_link_status = [{"linkState": "KO"}]
        cache_edge = {
            "edgeState": cache_edge_state,
            "edgeName": cache_edge_name,
            "enterpriseName": cache_test_enterprise_name,
            "links": cache_link_status,
        }
        self.test_pro_repo.reset_counter()
        self.test_pro_repo.inc(cache_edge)
        self.test_pro_repo.update_link(test_edge, test_link_status[0], cache_edge, cache_link_status[0])
        assert (
            REGISTRY.get_sample_value(
                "link_state_gauge", labels={"enterprise_name": test_enterprise_name, "state": "OK"}
            )
            == 1
        )
        assert (
            REGISTRY.get_sample_value(
                "link_state_gauge", labels={"enterprise_name": cache_test_enterprise_name, "state": "KO"}
            )
            == 0
        )

    def reset_counter_test(self):
        test_enterprise_name = "Test"
        test_edge_state = "Edge_OK"
        test_edge_name = "Test Edge Name"
        test_link_status = [{"linkState": "OK"}]
        test_edge = {
            "edgeState": test_edge_state,
            "edgeName": test_edge_name,
            "enterpriseName": test_enterprise_name,
            "links": test_link_status,
        }
        self.test_pro_repo.inc(test_edge)
        self.test_pro_repo.inc(test_edge)
        self.test_pro_repo.reset_counter()
        assert (
            REGISTRY.get_sample_value(
                "edge_state_gauge",
                labels={"enterprise_name": test_enterprise_name, "state": test_edge_state, "name": test_edge_name},
            )
            is None
        )
        assert (
            REGISTRY.get_sample_value(
                "edge_state_gauge", labels={"enterprise_name": test_enterprise_name, "state": "OK"}
            )
            is None
        )

    def start_prometheus_metrics_server_test(self):
        mock_server = application.repositories.prometheus_repository.start_http_server = Mock()
        self.test_pro_repo.start_prometheus_metrics_server()
        assert mock_server.called is True
