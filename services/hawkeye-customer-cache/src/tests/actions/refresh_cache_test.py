from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.actions import refresh_cache as refresh_cache_module
from application.actions.refresh_cache import RefreshCache
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from config import testconfig
from shortuuid import uuid
from tenacity import retry, stop_after_attempt

uuid_ = uuid()
uuid_mock = patch.object(refresh_cache_module, "uuid", return_value=uuid_)


# Drops the random nature of some retry calls, this is more convenient when testing
def retry_mock(attempts):
    def inner(*args, **kwargs):
        return retry(stop=stop_after_attempt(attempts), reraise=True)

    return inner


class TestRefreshCache:
    def instance_test(self):
        config = testconfig
        scheduler = Mock()
        storage_repository = Mock()
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        email_repository = Mock()

        refresh_cache = RefreshCache(
            config,
            scheduler,
            storage_repository,
            bruin_repository,
            hawkeye_repository,
            notifications_repository,
            email_repository,
        )

        assert refresh_cache._config == config
        assert refresh_cache._scheduler == scheduler
        assert refresh_cache._storage_repository == storage_repository
        assert refresh_cache._bruin_repository == bruin_repository
        assert refresh_cache._hawkeye_repository == hawkeye_repository
        assert refresh_cache._notifications_repository == notifications_repository
        assert refresh_cache._email_repository == email_repository

    @pytest.mark.asyncio
    async def schedule_cache_refresh_job_test(self, refresh_cache):
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(refresh_cache_module, "datetime", new=datetime_mock):
            with patch.object(refresh_cache_module, "timezone", new=Mock()):
                await refresh_cache.schedule_cache_refresh()

        refresh_cache._scheduler.add_job.assert_called_once_with(
            refresh_cache._refresh_cache,
            "interval",
            minutes=refresh_cache._config.REFRESH_CONFIG["refresh_map_minutes"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_refresh_cache",
        )

    @pytest.mark.asyncio
    async def schedule_cache_refresh_job_with_job_id_already_executing_test(self, refresh_cache):
        refresh_cache._scheduler.add_job = Mock(side_effect=ConflictingIdError("some-duplicated-id"))

        try:
            await refresh_cache.schedule_cache_refresh()
        except ConflictingIdError:
            refresh_cache._scheduler.add_job.assert_called_once_with(
                refresh_cache._refresh_cache,
                "interval",
                minutes=refresh_cache._config.REFRESH_CONFIG["refresh_map_minutes"],
                next_run_time=undefined,
                replace_existing=False,
                id="_refresh_cache",
            )

    @pytest.mark.asyncio
    async def refresh_cache_probe_test(self, refresh_cache, cache_probes_now, response_get_probes_down_ok):

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        refresh_cache._bruin_repository.filter_probe = AsyncMock(side_effect=[cache_probes_now[0], None])
        refresh_cache._hawkeye_repository.get_probes = AsyncMock(return_value=response_get_probes_down_ok)
        refresh_cache._storage_repository.set_hawkeye_cache = Mock()
        refresh_cache._partial_refresh_cache = AsyncMock()

        tenacity_retry_mock = patch.object(refresh_cache_module, "retry", side_effect=retry_mock(attempts=1))
        with patch.object(refresh_cache_module, "datetime", new=datetime_mock):
            with uuid_mock, tenacity_retry_mock:
                await refresh_cache._refresh_cache()
        refresh_cache._storage_repository.set_hawkeye_cache.assert_called_once()
        refresh_cache._bruin_repository.filter_probe.assert_called_with(
            response_get_probes_down_ok["body"][1],
        )

    @pytest.mark.asyncio
    async def refresh_cache_probes_list_500_test(
        self, refresh_cache, err_msg_refresh_retry_failed, response_500_probes
    ):
        refresh_cache._notifications_repository.send_slack_message = AsyncMock()
        err_msg_refresh_retry_failed["request_id"] = uuid_
        refresh_cache._hawkeye_repository.get_probes = AsyncMock(return_value=response_500_probes)

        refresh_cache._partial_refresh_cache = AsyncMock()
        refresh_cache._storage_repository.set_hawkeye_cache = Mock()

        tenacity_retry_mock = patch.object(refresh_cache_module, "retry", side_effect=retry_mock(attempts=1))
        with uuid_mock, tenacity_retry_mock:
            await refresh_cache._refresh_cache()
        refresh_cache._storage_repository.set_hawkeye_cache.assert_not_called()
        refresh_cache._notifications_repository.send_slack_message.assert_awaited_with(
            err_msg_refresh_retry_failed["message"]
        )

    @pytest.mark.asyncio
    async def refresh_cache_probes_list_failed_test(
        self, refresh_cache, err_msg_refresh_retry_failed, response_none_probes
    ):
        refresh_cache._notifications_repository.send_slack_message = AsyncMock()
        err_msg_refresh_retry_failed["request_id"] = uuid_
        refresh_cache._hawkeye_repository.get_probes = AsyncMock(return_value=response_none_probes)

        refresh_cache._partial_refresh_cache = AsyncMock()
        refresh_cache._storage_repository.set_hawkeye_cache = Mock()

        tenacity_retry_mock = patch.object(refresh_cache_module, "retry", side_effect=retry_mock(attempts=1))
        with uuid_mock, tenacity_retry_mock:
            await refresh_cache._refresh_cache()
        refresh_cache._storage_repository.set_hawkeye_cache.assert_not_called()
        refresh_cache._notifications_repository.send_slack_message.assert_awaited_with(
            err_msg_refresh_retry_failed["message"]
        )

    @pytest.mark.asyncio
    async def refresh_cache_probes_list_failed_with_several_consecutive_failures_test(
        self, refresh_cache, err_msg_refresh_cache_max_retries, response_none_probes
    ):
        err_msg_refresh_cache_max_retries["request_id"] = uuid_
        refresh_cache._notifications_repository.send_slack_message = AsyncMock()
        refresh_cache._hawkeye_repository.get_probes = AsyncMock(return_value=response_none_probes)

        refresh_cache._partial_refresh_cache = AsyncMock()
        refresh_cache._storage_repository.set_hawkeye_cache = Mock()

        retry_mock_fn = retry_mock(attempts=refresh_cache._config.REFRESH_CONFIG["attempts_threshold"])
        tenacity_retry_mock = patch.object(refresh_cache_module, "retry", side_effect=retry_mock_fn)
        with uuid_mock, tenacity_retry_mock:
            await refresh_cache._refresh_cache()

        refresh_cache._storage_repository.set_hawkeye_cache.assert_not_called()
        refresh_cache._notifications_repository.send_slack_message.assert_any_await(
            err_msg_refresh_cache_max_retries["message"]
        )

    @pytest.mark.asyncio
    async def send_mail_alert_test(
        self, refresh_cache, cache_probes_now, response_get_probes_down_ok, bruin_status_more_than_one_configuration
    ):

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        refresh_cache._bruin_repository.filter_probe = AsyncMock(side_effect=[cache_probes_now[0], None])
        refresh_cache._hawkeye_repository.get_probes = AsyncMock(return_value=response_get_probes_down_ok)
        refresh_cache._storage_repository.set_hawkeye_cache = Mock()
        refresh_cache._partial_refresh_cache = AsyncMock()
        refresh_cache._bruin_repository._serials_with_multiple_inventories = bruin_status_more_than_one_configuration
        refresh_cache._notifications_repository.send_slack_message = AsyncMock()

        tenacity_retry_mock = patch.object(refresh_cache_module, "retry", side_effect=retry_mock(attempts=1))
        with patch.object(refresh_cache_module, "datetime", new=datetime_mock):
            with uuid_mock, tenacity_retry_mock:
                await refresh_cache._refresh_cache()
        refresh_cache._storage_repository.set_hawkeye_cache.assert_called_once()
        refresh_cache._bruin_repository.filter_probe.assert_called_with(
            response_get_probes_down_ok["body"][1],
        )
        refresh_cache._notifications_repository.send_slack_message.assert_called()
        refresh_cache._email_repository.send_email.assert_called_once()
