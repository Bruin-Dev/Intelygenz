import datetime
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from application.repositories.lit_repository import LitRepository
from apscheduler.util import undefined

from application.repositories import lit_repository as lit_repo_module
from config import testconfig as config


class TestLitRepository:

    def instance_test(self):
        lit_client = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, config)

        assert lit_repo._lit_client == lit_client
        assert lit_repo._logger == logger
        assert lit_repo._scheduler == scheduler
        assert lit_repo._config == config

    def login_job_false_exec_on_start_test(self):
        lit_client = Mock()
        lit_client.login = Mock()
        logger = Mock()
        scheduler = Mock()
        configs = config

        lit_repo = LitRepository(lit_client, logger, scheduler, configs)
        with patch.object(lit_repo_module, 'timezone', new=Mock()):
            lit_repo.login_job()

        scheduler.add_job.assert_called_once_with(
            lit_client.login, 'interval',
            minutes=configs.LIT_CONFIG['login_ttl'],
            next_run_time=undefined,
            replace_existing=True,
            id='login',
        )

    def login_job_true_exec_on_start_test(self):
        lit_client = Mock()
        lit_client.login = Mock()
        logger = Mock()
        scheduler = Mock()
        configs = config

        lit_repo = LitRepository(lit_client, logger, scheduler, configs)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(lit_repo_module, 'datetime', new=datetime_mock):
            with patch.object(lit_repo_module, 'timezone', new=Mock()):
                lit_repo.login_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            lit_client.login, 'interval',
            minutes=configs.LIT_CONFIG['login_ttl'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='login',
        )

    def create_dispatch_test(self):
        lit_client = Mock()
        lit_client.create_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        lit_repo = LitRepository(lit_client, logger, scheduler, config)
        lit_repo.create_dispatch(payload)

        lit_client.create_dispatch.assert_called_with(payload)

    def cancel_dispatch_test(self):
        lit_client = Mock()
        lit_client.cancel_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()

        payload = {"dispatch_number": "D123"}

        lit_repo = LitRepository(lit_client, logger, scheduler, config)
        lit_repo.cancel_dispatch(payload)

        lit_client.cancel_dispatch.assert_called_with(payload)

    def get_dispatch_test(self):
        lit_client = Mock()
        lit_client.get_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()

        dispatch_number = "D123"
        lit_repo = LitRepository(lit_client, logger, scheduler, config)
        lit_repo.get_dispatch(dispatch_number)

        lit_client.get_dispatch.assert_called_with(dispatch_number)

    def get_all_dispatches_test(self):
        lit_client = Mock()
        lit_client.get_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, config)
        lit_repo.get_all_dispatches()

        lit_client.get_all_dispatches.assert_called_once()

    def update_dispatch_test(self):
        lit_client = Mock()
        lit_client.update_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        lit_repo = LitRepository(lit_client, logger, scheduler, config)
        lit_repo.update_dispatch(payload)

        lit_client.update_dispatch.assert_called_with(payload)

    def upload_file_test(self):
        lit_client = Mock()
        lit_client.upload_file = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}
        dispatch_number = "D123"
        file_name = "test.pdf"
        file_content = "application/pdf"

        lit_repo = LitRepository(lit_client, logger, scheduler, config)
        lit_repo.upload_file(dispatch_number, payload, file_name, file_content)

        lit_client.upload_file.assert_called_with(dispatch_number, payload, file_name, file_content)
