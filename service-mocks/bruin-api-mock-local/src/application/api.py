import json 

from flask import Blueprint, jsonify

api_blueprint = Blueprint("api", __name__)


# Email
@api_blueprint.route("/api/Email/<email_id>/tag/<tag_id>", methods=["POST"])
def post_tag(email_id, tag_id):
    return jsonify(""), 204


# Ticket
@api_blueprint.route("/api/Ticket/basic", methods=["GET"])
def get_tickets_basic_info():
    response_path = "src/application/responses/tickets_closed.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)
    return jsonify(json_content)


@api_blueprint.route("/api/Ticket/<ticket_id>/details", methods=["GET"])
def get_ticket_detail(ticket_id):
    response_path = "src/application/responses/ticket_detail.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)
    return jsonify(json_content)


# Inventory
@api_blueprint.route("/api/Inventory/", methods=["GET"])
def get_inventory():
    response_path = "src/application/responses/inventory.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)
    return jsonify(json_content)
