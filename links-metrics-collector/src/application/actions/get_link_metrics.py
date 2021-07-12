from datetime import datetime, timedelta


class GetLinkMetrics:
    def __init__(self, logger, config, mongo_client):
        self._logger = logger
        self._config = config
        self._mongo_client = mongo_client

    def get_links_metrics(self):
        # Basic example on how to retrieve data using a time filter.
        # A velo filter and a enterpriseId filter can be set here too when required.
        interval_start = (datetime.utcnow() - timedelta(seconds=30)).isoformat()
        interval_end = datetime.utcnow().isoformat()
        return self._mongo_client.get_from_interval(interval_start, interval_end)
