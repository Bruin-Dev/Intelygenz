import pytest
import asyncio
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc


class TestOrchestratorActions:
    def instance_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus_repository = Mock()
        scheduler = Mock()
        actions = Actions(test_bus, mock_logger, test_prometheus_repository, scheduler)
        assert actions._event_bus is test_bus
        assert actions._event_bus._logger is mock_logger
        assert actions._logger is mock_logger
        assert actions._prometheus_repository is test_prometheus_repository

    @pytest.mark.asyncio
    async def will_perform_scheduled_task_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus_repository = Mock()
        scheduler = AsyncIOScheduler(timezone=utc)
        actions = Actions(test_bus, mock_logger, test_prometheus_repository, scheduler)
        actions._send_edge_status_tasks = CoroutineMock()
        actions._prometheus_repository.set_cycle_total_edges = Mock()
        actions._prometheus_repository.reset_edges_counter = Mock()
        actions.set_edge_status_job(0.1, False)
        scheduler.start()
        await asyncio.sleep(0.3)
        scheduler.shutdown(wait=False)
        assert actions._send_edge_status_tasks.called
        assert actions._prometheus_repository.set_cycle_total_edges.called

    @pytest.mark.asyncio
    async def will_perform_scheduled_task_on_start_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus_repository = Mock()
        scheduler = AsyncIOScheduler(timezone=utc)
        actions = Actions(test_bus, mock_logger, test_prometheus_repository, scheduler)
        actions._send_edge_status_tasks = CoroutineMock()
        actions._prometheus_repository.set_cycle_total_edges = Mock()
        actions._prometheus_repository.reset_edges_counter = Mock()
        actions.set_edge_status_job(0.1, True)
        scheduler.start()
        await asyncio.sleep(0.1)
        scheduler.shutdown(wait=False)
        assert actions._send_edge_status_tasks.called
        assert actions._prometheus_repository.set_cycle_total_edges.called

    def start_prometheus_metrics_server_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_prometheus_repository = Mock()
        scheduler = Mock()
        actions = Actions(test_bus, mock_logger, test_prometheus_repository, scheduler)
        actions._prometheus_repository.start_prometheus_metrics_server = Mock()
        actions.start_prometheus_metrics_server()
        assert actions._prometheus_repository.start_prometheus_metrics_server.called is True
