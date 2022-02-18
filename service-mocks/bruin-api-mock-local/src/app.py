import logging

from flask import Flask

from application.login import login_blueprint
from application.api import api_blueprint


logger = logging.getLogger(__name__)

def create_app():
    flask_app = Flask(__name__)

    flask_app.register_blueprint(login_blueprint, url_prefix="/login")
    flask_app.register_blueprint(api_blueprint, url_prefix="/api")

    return flask_app


if __name__ == "__main__":
    logger.info("Running bruin-api-mock-local...")
    app = create_app()
    app.run(host="0.0.0.0", threaded=True, port=15001, debug=True, use_reloader=True)
