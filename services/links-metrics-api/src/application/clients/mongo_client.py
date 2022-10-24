import logging

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class MyMongoClient:
    def __init__(self, config):
        self._config = config
        self._client = self._connect_to_mongo()

    def _connect_to_mongo(self):
        username = self._config.MONGO_USERNAME
        password = self._config.MONGO_PASS
        url = self._config.MONGO_URL
        port = self._config.MONGO_PORT
        if self._config.CURRENT_ENVIRONMENT == "production":
            conn_string = (
                f"mongodb://{username}:{password}@{url}:{port}/velocloud?ssl=true&ssl_ca_certs="
                f"/rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference"
                f"=secondaryPreferred&retryWrites=false"
            )
        else:
            conn_string = f"mongodb://{username}:{password}@{url}:{port}/velocloud?authSource=admin"

        logger.info(
            f"Connecting to mongo using: {conn_string}, current environment: {self._config.CURRENT_ENVIRONMENT}"
        )
        try:
            client = AsyncIOMotorClient(conn_string)
            # ping the server here to check login was successful
            client.server_info()
            logger.info(f"Connected to mongo!")

        except Exception as err:
            logger.error(err)
            raise ValueError("Could not connect to MongoDB!")
        return client

    async def get_from_interval(self, interval_start, interval_end):
        # start and end are datetime isoformat objects
        logger.info(f"Trying to fetch data from {interval_start} to {interval_end}")
        db = self._client.get_default_database()

        cursor = db["links_series"].find(
            {
                "start_date": {
                    "$gte": int(interval_start),
                },
                "end_date": {"$lte": int(interval_end)},
            }
        )
        result = []
        async for doc in cursor:
            del doc["_id"]
            result.append(doc)

        logger.info(f"Data fetched from mongo successfully!")
        return result
