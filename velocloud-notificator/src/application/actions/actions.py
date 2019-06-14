from igz.packages.eventbus.eventbus import EventBus
from ast import literal_eval


class Actions:
    _config = None
    _event_bus = None
    _slack_repository = None
    _statistic_repository = None
    _logger = None
    _email_repository = None

    def __init__(self, config, event_bus: EventBus, slack_repository, statistic_repository, logger,
                 email_repository, scheduler):
        self._config = config
        self._event_bus = event_bus
        self._slack_repository = slack_repository
        self._statistic_repository = statistic_repository
        self._logger = logger
        self._email_repository = email_repository
        self._scheduler = scheduler

    def send_to_slack(self, msg):
        self._slack_repository.send_to_slack(msg)

    def store_stats(self, msg):
        self._statistic_repository.send_to_stats_client(msg)

    async def send_to_email_job(self, msg):
        decoded_msg = msg.decode('utf-8')
        msg_dict = literal_eval(decoded_msg)
        status = 500
        if msg_dict["message"] is not None and msg_dict["message"] != "":
            status = self._email_repository.send_to_email(msg_dict["message"])
        notification_response = {"request_id": msg_dict['request_id'], "status": status}
        await self._event_bus.publish_message("notification.email.response", repr(notification_response))

    def set_stats_to_slack_job(self):
        seconds = self._config.SLACK_CONFIG['time']
        self._scheduler.add_job(self._stats_to_slack_job, 'interval', seconds=seconds, replace_existing=True,
                                id='send_stats_to_slack_job')

    def _stats_to_slack_job(self):
        time = self._config.SLACK_CONFIG['time']
        sec_to_min = time / 60
        msg = self._statistic_repository._statistic_client.get_statistics(sec_to_min)
        if msg is not None:
            self.send_to_slack(msg)
        self._statistic_repository._statistic_client.clear_dictionaries()
        self._logger.info(f'{sec_to_min} minutes has passed')
