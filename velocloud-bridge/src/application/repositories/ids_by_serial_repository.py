from datetime import datetime

from apscheduler.util import undefined
from pytz import timezone


class IDsBySerialRepository:

    def __init__(self, config, logger, ids_by_serial_client, scheduler):
        self._config = config
        self._logger = logger
        self._ids_by_serial_client = ids_by_serial_client
        self._scheduler = scheduler

    def start_ids_by_serial_storage_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: creating IDs by Serial number dict')
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.VELOCLOUD_CONFIG['timezone']))
            self._logger.info(f'It will be executed now')
        self._scheduler.add_job(self._ids_by_serial_client.create_id_by_serial_dict, 'interval',
                                days=self._config.VELOCLOUD_CONFIG['days_to_create_dict'],
                                next_run_time=next_run_time, replace_existing=True,
                                id='create_id_by_serial_dict')

    def search_for_edge_id_by_serial(self, serial):
        return self._ids_by_serial_client.search_for_edge_id_by_serial(serial)
