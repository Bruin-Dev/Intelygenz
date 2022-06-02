import abc

from delivery.http.blueprints import health, statistics
from flask import Flask


class IHTTPServer(metaclass=abc.ABCMeta):
    def __init__(self, config, logger, adapters, use_cases) -> None:
        self.config = config
        self.logger = logger
        self.adapters = adapters
        self.use_cases = use_cases

        self.adapters.wire(modules=[statistics])
        self.use_cases.wire(modules=[statistics])

        self.client = Flask(self.config["server"]["name"])
        self.client.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

        self.initialize()

    @abc.abstractmethod
    def status(self):
        pass


class FlaskServer(IHTTPServer):
    def initialize(self):
        from delivery.http.handlers.error_handler import constructor_error_handler
        from delivery.http.handlers.method_not_allowed import constructor_send_method_not_found
        from delivery.http.handlers.not_found_handler import constructor_not_found
        from flask_cors import CORS
        from flask_log_request_id import RequestID

        CORS(self.client)
        RequestID(self.client)

        with self.client.app_context():
            # Force to use our own logger
            self.client.logger = self.logger

            # Load endpoints from constructors
            health_blueprint = health.construct_health_check_blueprint(self.config["server"]["version"])

            # Endpoints
            self.client.register_blueprint(blueprint=health_blueprint, url_prefix=self.config["server"]["root_path"])
            self.client.register_blueprint(statistics.get_blueprint(), url_prefix=self.config["server"]["root_path"])

            # Error handler
            self.client.register_error_handler(
                code_or_exception=Exception, f=constructor_error_handler(logger=self.client.logger)
            )
            self.client.register_error_handler(
                code_or_exception=404, f=constructor_not_found(logger=self.client.logger)
            )
            self.client.register_error_handler(
                code_or_exception=405, f=constructor_send_method_not_found(logger=self.client.logger)
            )

            # Other options
            self.client.url_map.strict_slashes = False

    def start(self):
        is_dev = self.config["current_environment"] == "dev"
        self.client.run(
            host="0.0.0.0", port=self.config["server"]["port"], threaded=True, use_reloader=is_dev, debug=is_dev
        )

    def status(self):
        self.logger.info("Flask HTTP Server Running")
