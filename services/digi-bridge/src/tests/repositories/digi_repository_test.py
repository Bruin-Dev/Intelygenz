import datetime
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from application.repositories import digi_repository as digi_repository_module
from application.repositories.digi_repository import DiGiRepository
from apscheduler.util import undefined
from asynctest import CoroutineMock
from config import testconfig as config


class TestDiGiRepository:
    def instance_test(self):
        logger = Mock()
        scheduler = Mock()
        digi_client = Mock()

        digi_repository = DiGiRepository(config, logger, scheduler, digi_client)

        assert digi_repository._config == config
        assert digi_repository._logger == logger
        assert digi_repository._scheduler == scheduler
        assert digi_repository._digi_client == digi_client

    @pytest.mark.asyncio
    async def login_job_false_exec_on_start_test(self):
        logger = Mock()
        scheduler = Mock()
        digi_client = Mock()
        digi_client.login = Mock()

        digi_repository = DiGiRepository(config, logger, scheduler, digi_client)

        with patch.object(digi_repository_module, "timezone", new=Mock()):
            await digi_repository.login_job()

        digi_repository._scheduler.add_job.assert_called_once_with(
            digi_client.login,
            "interval",
            minutes=config.DIGI_CONFIG["login_ttl"],
            next_run_time=undefined,
            replace_existing=True,
            id="login",
        )

    @pytest.mark.asyncio
    async def login_job_true_exec_on_start_test(self):
        logger = Mock()
        scheduler = Mock()
        digi_client = Mock()
        digi_client.login = Mock()

        digi_repository = DiGiRepository(config, logger, scheduler, digi_client)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(digi_repository_module, "datetime", new=datetime_mock):
            with patch.object(digi_repository_module, "timezone", new=Mock()):
                await digi_repository.login_job(exec_on_start=True)

        digi_repository._scheduler.add_job.assert_called_once_with(
            digi_client.login,
            "interval",
            minutes=config.DIGI_CONFIG["login_ttl"],
            next_run_time=next_run_time,
            replace_existing=True,
            id="login",
        )

    @pytest.mark.asyncio
    async def reboot_test(self):
        logger = Mock()
        scheduler = Mock()

        digi_client = Mock()
        digi_client.reboot = CoroutineMock()

        request_id = "test_id"

        payload = {"igzID": request_id, "velo_serial": 123, "ticket": 321}
        digi_repository = DiGiRepository(config, logger, scheduler, digi_client)

        reboot_return = await digi_repository.reboot(payload)

        digi_client.reboot.assert_awaited_once_with(payload)

    @pytest.mark.asyncio
    async def get_digi_recovery_logs_test(self):
        logger = Mock()
        scheduler = Mock()

        digi_client = Mock()
        digi_client.get_digi_recovery_logs = CoroutineMock()

        request_id = "test_id"

        payload = {"igzID": request_id}
        digi_repository = DiGiRepository(config, logger, scheduler, digi_client)

        recovery_logs = await digi_repository.get_digi_recovery_logs(payload)

        digi_client.get_digi_recovery_logs(payload)
