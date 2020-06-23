import datetime
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from application.repositories.cts_repository import CtsRepository
from apscheduler.util import undefined

from application.clients.cts_client import CtsClient
from application.repositories import cts_repository as cts_repo_module
from config import testconfig as config


class TestCTSRepository:

    def instance_test(self, cts_client):
        logger = Mock()
        scheduler = Mock()
        config = Mock()

        cts_repo = CtsRepository(cts_client, logger, scheduler, config)

        assert cts_repo._cts_client == cts_client
        assert cts_repo._logger == logger
        assert cts_repo._scheduler == scheduler
        assert cts_repo._config == config

    def login_job_false_exec_on_start_test(self, cts_client, cts_repository):
        cts_client.login = Mock()

        with patch.object(cts_repo_module, 'timezone', new=Mock()):
            cts_repository.login_job()

        cts_repository._scheduler.add_job.assert_called_once_with(
            cts_client.login, 'interval',
            minutes=cts_repository._config.CTS_CONFIG['login_ttl'],
            next_run_time=undefined,
            replace_existing=True,
            id='login',
        )

    def login_job_true_exec_on_start_test(self, cts_client, cts_repository):
        cts_client.login = Mock()
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(cts_repo_module, 'datetime', new=datetime_mock):
            with patch.object(cts_repo_module, 'timezone', new=Mock()):
                cts_repository.login_job(exec_on_start=True)

        cts_repository._scheduler.add_job.assert_called_once_with(
            cts_client.login, 'interval',
            minutes=cts_repository._config.CTS_CONFIG['login_ttl'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='login',
        )

    def create_dispatch_test(self):
        logger = Mock()
        scheduler = Mock()
        config = Mock()

        cts_client = CtsClient(logger, config)
        cts_client.create_dispatch = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        cts_repo = CtsRepository(cts_client, logger, scheduler, config)

        cts_repo.create_dispatch(payload)

        cts_client.create_dispatch.assert_called_with(payload)

    def get_dispatch_test(self, cts_repository, cts_client):
        cts_client.get_dispatch = Mock()

        dispatch_number = "S-12345"
        cts_repository.get_dispatch(dispatch_number)

        cts_client.get_dispatch.aseert_called_with(dispatch_number)

    def get_all_dispatch_test(self, cts_repository, cts_client):
        cts_client.get_dispatches = Mock()

        cts_repository.get_all_dispatches()

        cts_client.get_dispatches.aseert_called_once()

    def update_dispatch_test(self, cts_repository, cts_client):
        cts_client.update_dispatch = Mock()
        dispatch_number = "S-12345"
        payload = {"Request_Dispatch": {"test": "dispatch"}}

        cts_repository.update_dispatch(dispatch_number, payload)

        cts_client.update_dispatch.assert_called_with(dispatch_number, payload)
