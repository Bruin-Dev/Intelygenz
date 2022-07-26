from pymongo import MongoClient
from pymongo import errors as pymongo_errors


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
        if self._config.CURRENT_ENVIRONMENT == "production":
            conn_string = (
                f"mongodb://{username}:{password}@{url}:{port}/velocloud?ssl=true&ssl_ca_certs="
                f"/rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference"
                f"=secondaryPreferred&retryWrites=false"
            )
        else:
            conn_string = f"mongodb://{username}:{password}@{url}:{port}/velocloud?authSource=admin"

        self._logger.info(
            f"Connecting to mongo using: {conn_string}, " f"current environment: {self._config.CURRENT_ENVIRONMENT}"
        )
        try:
            client = MongoClient(conn_string)
            # ping the server here to check login was successful
            client.server_info()
            self._logger.info(f"Connected to mongo!")

        except pymongo_errors.ServerSelectionTimeoutError as err:
            self._logger.error(err)
            raise ValueError("Could not connect to MongoDB!")
        return client

    def insert(self, json_data: dict):
        self._logger.info(f"Inserting data in mongo...")
        db = self._client.get_default_database()
        list_collections = db.collection_names()
        if "links_series" in list_collections:
            self._logger.info(f"The collection tickets on database links_series exists on mongodb.")
        else:
            self._logger.info(f"The collection tickets on database links_series does not exists on mongodb.")
            db.create_collection("links_series")
        result = db["links_series"].insert_one(json_data)
        self._logger.info(f"ACK of inserting: {result.acknowledged}")
        return result.inserted_id
