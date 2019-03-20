import pytest
import asyncio
from unittest.mock import Mock
from asynctest import CoroutineMock
from application.actions.actions import Actions
from igz.packages.eventbus.eventbus import EventBus


class TestOverseerActions:
    def instance_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        assert actions._event_bus is test_bus
        assert actions._velocloud_repository is velocloud_repo
        assert actions._event_bus._logger is mock_logger
        assert actions._logger is mock_logger

    @pytest.mark.asyncio
    async def will_generate_tasks_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        test_bus.publish_message = CoroutineMock()
        velocloud_repo = Mock()
        edges = ["task1", "task2"]
        velocloud_repo.get_all_enterprises_edges_with_host = Mock(return_value=edges)
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        actions._logger.info = Mock()
        await actions._send_edge_status_tasks()
        assert test_bus.publish_message.call_count is len(edges)
        assert actions._logger.info.called

    @pytest.mark.asyncio
    async def will_perform_scheduled_task_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        actions._send_edge_status_tasks = CoroutineMock()
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(actions.send_edge_status_task_interval(0.1, False))
        await asyncio.sleep(0.2)
        task.cancel()
        loop.stop()
        assert actions._send_edge_status_tasks.called

    @pytest.mark.asyncio
    async def will_perform_scheduled_task_on_start_test(self):
        mock_logger = Mock()
        test_bus = EventBus(logger=mock_logger)
        velocloud_repo = Mock()
        actions = Actions(test_bus, velocloud_repo, mock_logger)
        actions._send_edge_status_tasks = CoroutineMock()
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(actions.send_edge_status_task_interval(100, True))
        await asyncio.sleep(0.1)
        task.cancel()
        loop.stop()
        assert actions._send_edge_status_tasks.called
