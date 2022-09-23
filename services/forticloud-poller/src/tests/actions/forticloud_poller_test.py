from datetime import datetime
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined

from application.actions import forticloud_poller as forticloud_poller_module
from config import testconfig


class TestForticloudPoller:
    @pytest.mark.asyncio
    async def start_forticloud_poller_with_no_exec_on_start_test(self, forticloud_poller):
        forticloud_poller._scheduler.add_job = Mock()

        await forticloud_poller.start_forticloud_poller()

        forticloud_poller._scheduler.add_job.assert_called_once_with(
            forticloud_poller._forticloud_poller_process,
            "interval",
            minutes=forticloud_poller._config.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=undefined,
            replace_existing=False,
            id="_forticloud_poller_process",
        )

    @pytest.mark.asyncio
    async def start_forticloud_poller_with_exec_on_start_test(self, forticloud_poller):
        forticloud_poller._scheduler.add_job = Mock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(forticloud_poller_module, "datetime", new=datetime_mock):
            with patch.object(forticloud_poller_module, "timezone", new=Mock()):
                await forticloud_poller.start_forticloud_poller(exec_on_start=True)

        forticloud_poller._scheduler.add_job.assert_called_once_with(
            forticloud_poller._forticloud_poller_process,
            "interval",
            minutes=forticloud_poller._config.MONITOR_CONFIG["monitoring_minutes_interval"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_forticloud_poller_process",
        )

    @pytest.mark.asyncio
    async def start_forticloud_poller_with_job_id_already_executing_test(self, forticloud_poller):
        job_id = "some-duplicated-id"
        exception_instance = ConflictingIdError(job_id)
        forticloud_poller._scheduler.add_job = Mock(side_effect=exception_instance)

        try:
            await forticloud_poller.start_forticloud_poller()
        except ConflictingIdError:
            forticloud_poller._scheduler.add_job.assert_called_once_with(
                forticloud_poller._forticloud_poller_process,
                "interval",
                minutes=forticloud_poller._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                next_run_time=undefined,
                replace_existing=False,
                id="_forticloud_poller_process",
            )

    @pytest.mark.asyncio
    async def _forticloud_poller_process_ok_test(self, forticloud_poller):
        redis_response = [
            {"data": "some-data", "other-data": "some-other-data", "some_id": 1},
            {"data-2": "some-data-2", "other-data-2": "some-other-data-2", "some_id": 2},
        ]
        redis_response2 = [
            {"data-3": "some-data", "other-data": "some-other-data", "some_id": 1},
            {"data-2": "some-data-2", "other-data-2": "some-other-data-2", "some_id": 2},
        ]
        forticloud_poller._redis_repository.get_list_access_points_of_redis = Mock(return_value=redis_response)
        forticloud_poller._redis_repository.get_list_switches_of_redis = Mock(return_value=redis_response2)
        forticloud_poller._process_data = AsyncMock()

        await forticloud_poller._forticloud_poller_process()

        forticloud_poller._process_data.assert_has_calls(
            [call(redis_response, target="aps"), call(redis_response2, target="switches")]
        )

    @pytest.mark.asyncio
    async def _forticloud_poller_process_empty_list_ok_test(self, forticloud_poller):
        redis_response = []
        redis_response2 = [
            {"data-3": "some-data", "other-data": "some-other-data", "some_id": 1},
            {"data-2": "some-data-2", "other-data-2": "some-other-data-2", "some_id": 2},
        ]
        forticloud_poller._redis_repository.get_list_access_points_of_redis = Mock(return_value=redis_response)
        forticloud_poller._redis_repository.get_list_switches_of_redis = Mock(return_value=redis_response2)
        forticloud_poller._process_data = AsyncMock()
        forticloud_poller._notifications_repository.send_slack_message = AsyncMock()

        await forticloud_poller._forticloud_poller_process()

        forticloud_poller._process_data.assert_has_calls([call(redis_response2, target="switches")])
        forticloud_poller._notifications_repository.send_slack_message.assert_awaited()

    @pytest.mark.asyncio
    async def _forticloud_process_data_ok_test(self, forticloud_poller):
        data = [
            {"data": "some-data", "other-data": "some-other-data", "some_id": 1},
            {"data-2": "some-data-2", "other-data-2": "some-other-data-2", "some_id": 2},
        ]
        forticloud_poller._publish_forticloud_data = AsyncMock()

        await forticloud_poller._process_data(data, target="whatever")

        forticloud_poller._publish_forticloud_data.assert_has_calls(
            [call(data[0], "whatever"), call(data[1], "whatever")]
        )

    @pytest.mark.asyncio
    async def _forticloud_publish_forticloud_data_ok_test(self, forticloud_poller):
        data = {"data": "some-data", "other-data": "some-other-data", "some_id": 1}
        forticloud_poller._nats_client.publish_message = AsyncMock()

        await forticloud_poller._publish_forticloud_data(data, target="whatever")

        forticloud_poller._nats_client.publish_message.assert_awaited_with("forticloud.whatever", {"data": data})
