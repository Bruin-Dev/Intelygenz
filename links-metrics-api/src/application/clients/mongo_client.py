from motor.motor_asyncio import AsyncIOMotorClient


class MyMongoClient:

    def __init__(self, logger, config):
        self._logger = logger
        self._config = config
        self._client = self._connect_to_mongo()

    def _connect_to_mongo(self):
        username = self._config.MONGO_USERNAME
        password = self._config.MONGO_PASS
        url = self._config.MONGO_URL
        port = self._config.MONGO_PORT
        if self._config.ENVIRONMENT_NAME == "production":
            conn_string = f'mongodb://{username}:{password}@{url}:{port}/velocloud?ssl=true&ssl_ca_certs=' \
                          f'/service/app/rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference' \
                          f'=secondaryPreferred&retryWrites=false'
        else:
            conn_string = f'mongodb://{username}:{password}@{url}:{port}/velocloud?authSource=admin'

        self._logger.info(f'Connecting to mongo using: {conn_string}, '
                          f'current environment: {self._config.ENVIRONMENT_NAME}')
        try:
            client = AsyncIOMotorClient(conn_string)
            # ping the server here to check login was successful
            client.server_info()
            self._logger.info(f'Connected to mongo!')

        except Exception as err:
            self._logger.error(err)
            raise ValueError('Could not connect to MongoDB!')
        return client

    async def get_from_interval(self, interval_start, interval_end):
        # start and end are datetime isoformat objects
        self._logger.info(f'Trying to fetch data from {interval_start} to {interval_end}')
        db = self._client.get_default_database()

        cursor = db["links_metrics"].find({"created_date": {
            "$gte": interval_start,
            "$lt": interval_end
        }})
        result = []

        for doc in await cursor.to_list(None):
            del doc["_id"]

            oreilly_metrics = []
            for link_metrics in doc['metrics']:
                if link_metrics['link']['enterpriseId'] == self._config.ENTERPRISE_ID:
                    del link_metrics['link']['host']
                    oreilly_metrics.append(link_metrics)

            doc['metrics'] = oreilly_metrics
            result.append(doc)

        self._logger.info(f'Data fetched from mongo successfully!')
        return result
