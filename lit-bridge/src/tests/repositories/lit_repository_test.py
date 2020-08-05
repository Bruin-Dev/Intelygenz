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
        redis_client = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)

        assert lit_repo._lit_client == lit_client
        assert lit_repo._logger == logger
        assert lit_repo._scheduler == scheduler
        assert lit_repo._config == config

    def login_job_false_exec_on_start_test(self, instance_lit_repository):
        instance_lit_repository._lit_client._login = Mock()

        with patch.object(lit_repo_module, 'timezone', new=Mock()):
            instance_lit_repository.login_job()

        instance_lit_repository._scheduler.add_job.assert_called_once_with(
            instance_lit_repository._lit_client.login, 'interval',
            minutes=instance_lit_repository._config.LIT_CONFIG['login_ttl'],
            next_run_time=undefined,
            replace_existing=True,
            id='login',
        )

    def login_job_true_exec_on_start_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.login = Mock()

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(lit_repo_module, 'datetime', new=datetime_mock):
            with patch.object(lit_repo_module, 'timezone', new=Mock()):
                instance_lit_repository.login_job(exec_on_start=True)

        instance_lit_repository._scheduler.add_job.assert_called_once_with(
            instance_lit_repository._lit_client.login, 'interval',
            minutes=instance_lit_repository._config.LIT_CONFIG['login_ttl'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='login',
        )

    def create_dispatch_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.create_dispatch = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        instance_lit_repository.create_dispatch(payload)
        instance_lit_repository._lit_client.create_dispatch.assert_called_with(payload)

    def get_dispatch_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.get_dispatch = Mock()

        dispatch_number = "D123"

        instance_lit_repository.get_dispatch(dispatch_number)
        instance_lit_repository._lit_client.get_dispatch.assert_called_with(dispatch_number)

    def cancel_dispatch_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.cancel_dispatch = Mock()

        dispatch_number = "D123"

        instance_lit_repository.cancel_dispatch(dispatch_number)
        instance_lit_repository._lit_client.cancel_dispatch.assert_called_with(dispatch_number)

    def get_all_dispatches_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.get_dispatch = Mock()

        instance_lit_repository.get_all_dispatches()

        instance_lit_repository._lit_client.get_all_dispatches.assert_called_once()

    def update_dispatch_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.update_dispatch = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        instance_lit_repository.update_dispatch(payload)
        instance_lit_repository._lit_client.update_dispatch.assert_called_with(payload)

    def upload_file_test(self, instance_lit_repository):
        instance_lit_repository._lit_client.upload_file = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}
        dispatch_number = "D123"
        file_name = "test.pdf"
        file_content = "application/pdf"

        instance_lit_repository.upload_file(dispatch_number, payload, file_name, file_content)
        instance_lit_repository._lit_client.upload_file.assert_called_with(dispatch_number, payload, file_name,
                                                                           file_content)

    def filter_dispatches_test(self, instance_lit_repository):
        dispatches_response = [{'Dispatch_Number': 123}]
        dispatches = {'DispatchList': dispatches_response}

        instance_lit_repository._redis_client.get = Mock(return_value={'body': 'ok', 'status': 200})

        response = instance_lit_repository.filter_dispatches(dispatches)

        assert response == dispatches_response

    def filter_dispatches_with_empty_redis_test(self, instance_lit_repository):
        dispatches_response = [{'Dispatch_Number': 123}]
        dispatches = {'DispatchList': dispatches_response}

        instance_lit_repository._redis_client.get = Mock(return_value=None)

        response = instance_lit_repository.filter_dispatches(dispatches)

        assert response == []

    def filter_dispatches_empty_dispatches_test(self, instance_lit_repository):
        dispatches = {}

        instance_lit_repository._redis_client.get = Mock(return_value=None)

        response = instance_lit_repository.filter_dispatches(dispatches)

        assert response == []
