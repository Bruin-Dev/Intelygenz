from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories.ids_by_serial_repository import IDsBySerialRepository
from apscheduler.util import undefined

from application.repositories import ids_by_serial_repository as id_by_serial_repository_module
from config import testconfig


class TestIdsBySerialRepository:

    def instance_test(self):
        config = Mock()
        mock_logger = Mock()
        ids_by_serial_client = Mock()
        scheduler = Mock()
        ids_by_serial_repo = IDsBySerialRepository(config, mock_logger, ids_by_serial_client, scheduler)
        assert ids_by_serial_repo._config == config
        assert ids_by_serial_repo._logger == mock_logger
        assert ids_by_serial_repo._ids_by_serial_client == ids_by_serial_client
        assert ids_by_serial_repo._scheduler == scheduler

    @pytest.mark.asyncio
    async def start_ids_by_serial_storage_job_with_exec_on_start_test(self):
        config = testconfig
        mock_logger = Mock()
        ids_by_serial_client = Mock()
        scheduler = Mock()
        ids_by_serial_repo = IDsBySerialRepository(config, mock_logger, ids_by_serial_client, scheduler)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(id_by_serial_repository_module, 'datetime', new=datetime_mock):
            with patch.object(id_by_serial_repository_module, 'timezone', new=Mock()):
                ids_by_serial_repo.start_ids_by_serial_storage_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            ids_by_serial_client.create_id_by_serial_dict, 'interval',
            days=config.VELOCLOUD_CONFIG['days_to_create_dict'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='create_id_by_serial_dict',
        )

    @pytest.mark.asyncio
    async def start_ids_by_serial_storage_job_without_exec_on_start_test(self):
        config = testconfig
        mock_logger = Mock()
        ids_by_serial_client = Mock()
        scheduler = Mock()
        ids_by_serial_repo = IDsBySerialRepository(config, mock_logger, ids_by_serial_client, scheduler)

        with patch.object(id_by_serial_repository_module, 'timezone', new=Mock()):
            ids_by_serial_repo.start_ids_by_serial_storage_job()

        scheduler.add_job.assert_called_once_with(
            ids_by_serial_client.create_id_by_serial_dict, 'interval',
            days=config.VELOCLOUD_CONFIG['days_to_create_dict'],
            next_run_time=undefined,
            replace_existing=True,
            id='create_id_by_serial_dict',
        )

    def search_for_edge_id_by_serial_test(self):
        config = Mock()
        mock_logger = Mock()

        serial = 'VC05'

        ids_by_serial_client = Mock()
        ids_by_serial_client.search_for_edge_id_by_serial = Mock()

        scheduler = Mock()
        ids_by_serial_repo = IDsBySerialRepository(config, mock_logger, ids_by_serial_client, scheduler)

        ids_by_serial_repo.search_for_edge_id_by_serial(serial)

        ids_by_serial_client.search_for_edge_id_by_serial.assert_called_once_with(serial)
