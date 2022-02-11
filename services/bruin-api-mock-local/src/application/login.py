import json

from flask import Blueprint, request, jsonify

login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("identity/connect/token", methods=["POST"])
def identity_connect_token():
    response_path = "src/application/responses/login.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)
    return jsonify(json_content)

