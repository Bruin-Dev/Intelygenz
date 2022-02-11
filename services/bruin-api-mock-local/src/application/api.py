from flask import Blueprint, request, jsonify

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("dummy", methods=["POST"])
def dummy():
    print(request, request.data, request.headers)
    return jsonify({"response": request.data})
