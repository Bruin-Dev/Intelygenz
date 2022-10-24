import logging

from pymongo import MongoClient
from pymongo import errors as pymongo_errors

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
                f"mongodb://{username}:{password}@{url}:{port}/velocloud?ssl=true&tlsCAFile="
                f"/rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference"
                f"=secondaryPreferred&retryWrites=false"
            )
        else:
            conn_string = f"mongodb://{username}:{password}@{url}:{port}/velocloud?authSource=admin"

        logger.info(
            f"Connecting to mongo using: {conn_string}, current environment: {self._config.CURRENT_ENVIRONMENT}"
        )
        try:
            client = MongoClient(conn_string)
            # ping the server here to check login was successful
            client.server_info()
            logger.info(f"Connected to mongo!")

        except pymongo_errors.ServerSelectionTimeoutError as err:
            logger.error(err)
            raise ValueError("Could not connect to MongoDB!")
        return client

    def insert(self, json_data: dict):
        logger.info(f"Inserting data in mongo...")
        db = self._client.get_default_database()
        list_collections = db.list_collection_names()
        if "links_series" in list_collections:
            logger.info(f"The collection tickets on database links_series exists on mongodb.")
        else:
            logger.info(f"The collection tickets on database links_series does not exists on mongodb.")
            db.create_collection("links_series")
        result = db["links_series"].insert_one(json_data)
        logger.info(f"ACK of inserting: {result.acknowledged}")
        return result.inserted_id
