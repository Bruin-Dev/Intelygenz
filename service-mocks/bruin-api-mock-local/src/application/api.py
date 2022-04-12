import json

from flask import Blueprint, jsonify, request

api_blueprint = Blueprint("api", __name__)


# Email
@api_blueprint.route("/api/Email/<email_id>/tag/<tag_id>", methods=["POST"])
def post_tag(email_id, tag_id):
    return jsonify({}, 204)


@api_blueprint.route("/api/Email/<email_id>/link/ticket/<ticket_id>", methods=["POST"])
def post_email_link_ticket(email_id, ticket_id):
    return jsonify({}, 204)


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


@api_blueprint.route("/api/Ticket/repair", methods=["POST"])
def post_ticket_repair():
    response_path = "src/application/responses/create_repair_ticket.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)
    return jsonify(json_content)


@api_blueprint.route("/api/Ticket/<ticket_id>/notes/advanced", methods=["POST"])
def post_notes_advanced(ticket_id):
    response_path = "src/application/responses/create_note.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)
    return jsonify(json_content)


# Inventory
@api_blueprint.route("/api/Inventory/", methods=["GET"])
def get_inventory():
    response_path = "src/application/responses/inventory.json"
    with open(response_path) as file_object:
        json_content = json.load(file_object)

    args_dict = request.args.to_dict()
    service_number = args_dict.get("ServiceNumber")
    if service_number:
        json_content['documents'][0]['ServiceNumber'] = service_number

    return jsonify(json_content)
