from flask import Blueprint, jsonify

ENDPOINT = "/_health"


def construct_health_check_blueprint(version):

    health_check = Blueprint("health_check", __name__, template_folder="blueprints")

    @health_check.route(ENDPOINT)
    def health_check_endpoint():
        return jsonify({"version": version})

    return health_check
