import asyncio

from typing import List


class BruinRepository:

    def __init__(self, logger, bruin_client):
        self._logger = logger
        self._bruin_client = bruin_client

    async def get_all_filtered_tickets(self, params, ticket_status):
        response = dict.fromkeys(["body", "status"])
        response['body'] = []
        response['status'] = 200

        futures = [
            self._get_tickets_by_status(status, params.copy(), response)
            for status in ticket_status
        ]
        try:
            results = await asyncio.gather(*futures)
        except Exception as error:
            return response

        tickets = sum(results, [])  # This joins all elements in "results"
        response['body'] = list({ticket['ticketID']: ticket for ticket in tickets}.values())

        return response

    async def _get_tickets_by_status(self, status, params, response):
        params["TicketStatus"] = status
        status_ticket_list = await self._bruin_client.get_all_tickets(params)
        response['status'] = status_ticket_list['status']
        if status_ticket_list["status"] not in range(200, 300):
            return []

        return status_ticket_list["body"]

    async def get_ticket_details(self, ticket_id):
        return await self._bruin_client.get_ticket_details(ticket_id)

    async def post_ticket_note(self, ticket_id, note, *, service_numbers: list = None):
        payload = {
            "note": note
        }

        if service_numbers:
            payload['serviceNumbers'] = service_numbers

        return await self._bruin_client.post_ticket_note(ticket_id, payload)

    async def post_multiple_ticket_notes(self, ticket_id: int, notes: List[dict]) -> dict:
        payload = {
            'notes': [],
        }

        for note in notes:
            note_for_payload = {
                'noteValue': note['text'],
            }

            if 'service_number' in note.keys():
                note_for_payload['serviceNumber'] = note['service_number']

            if 'detail_id' in note.keys():
                note_for_payload['detailId'] = note['detail_id']

            if note.get('is_private'):
                note_for_payload['noteType'] = 'CON'  # Private note
            else:
                note_for_payload['noteType'] = 'ADN'  # Public, standard note

            payload['notes'].append(note_for_payload)

        response = await self._bruin_client.post_multiple_ticket_notes(ticket_id, payload)

        if response['status'] not in range(200, 300):
            return response

        response['body'] = response['body']['ticketNotes']
        return response

    async def post_ticket(self, payload):
        return await self._bruin_client.post_ticket(payload)

    async def open_ticket(self, ticket_id, detail_id):
        payload = {"Status": "O"}
        return await self._bruin_client.update_ticket_status(ticket_id, detail_id, payload)

    async def resolve_ticket(self, ticket_id, detail_id):
        payload = {"Status": "R"}
        return await self._bruin_client.update_ticket_status(ticket_id, detail_id, payload)

    async def get_management_status(self, filters):
        response = await self._bruin_client.get_management_status(filters)

        if response["status"] not in range(200, 300):
            return response

        if "attributes" in response["body"].keys():
            management_status = [attribute["value"] for attribute in response["body"]["attributes"] if
                                 attribute["key"] == "Management Status"]
            if len(management_status) > 0:
                management_status = management_status[0]
            else:
                management_status = None

            response["body"] = management_status

        return response

    async def post_outage_ticket(self, client_id, service_number):
        response = await self._bruin_client.post_outage_ticket(client_id, service_number)

        status_code = response['status']
        if not (status_code in range(200, 300) or status_code == 409 or status_code == 471):
            return response

        response['body'] = response['body']['ticketId']
        return response

    async def get_client_info(self, filters):
        response = await self._bruin_client.get_client_info(filters)

        if response["status"] not in range(200, 300):
            return response

        documents = response["body"].get("documents")
        response_body = {"client_id": None,
                         "client_name": None}

        if documents:
            # We only want the current active company for the device if there's one
            active_status = [status for status in documents if
                             status["status"] == "A" and status["serviceNumber"] in filters["service_number"]]
            if active_status:
                # There should be only one active status per serial
                client_id = active_status[0].get("clientID")
                client_name = active_status[0].get("clientName")
                response_body = {"client_id": client_id,
                                 "client_name": client_name}

        response["body"] = response_body
        return response

    async def get_next_results_for_ticket_detail(self, ticket_id, detail_id, service_number):
        get_work_queues_filters = {
            "ServiceNumber": service_number,
            "DetailId": detail_id,
        }

        next_results_response = await self._bruin_client.get_possible_detail_next_result(
            ticket_id, get_work_queues_filters
        )
        return next_results_response

    async def change_detail_work_queue(self, ticket_id, filters):
        service_number = filters["service_number"]
        ticket_detail_id = filters["detail_id"]

        get_work_queues_filters = {
            "ServiceNumber": service_number,
            "DetailId": ticket_detail_id,
        }

        possible_work_queues_response = await self._bruin_client.get_possible_detail_next_result(
            ticket_id, get_work_queues_filters
        )
        possible_work_queues_response_body = possible_work_queues_response['body']
        possible_work_queues_response_status = possible_work_queues_response['status']
        if possible_work_queues_response_status not in range(200, 300):
            return {
                'body': f'Error while claiming possible work queues for ticket {ticket_id} and filters '
                        f'{get_work_queues_filters}: {possible_work_queues_response_body}',
                'status': possible_work_queues_response_status,
            }

        work_queues = possible_work_queues_response_body['nextResults']
        if not work_queues:
            return {
                'body': f'No work queues were found for ticket {ticket_id} and filters {get_work_queues_filters}',
                'status': 404,
            }

        queue_name = filters["queue_name"]
        work_queue_id = None
        for possible_work_queue in work_queues:
            if possible_work_queue["resultName"] == queue_name:
                work_queue_id = possible_work_queue["resultTypeId"]
                break

        if not work_queue_id:
            result = {
                "body": f'No work queue with name {queue_name} was found using ticket ID {ticket_id} and '
                        f'filters {get_work_queues_filters}',
                "status": 404
            }
            return result

        put_work_queue_payload = {
            "details": [
                {
                    "detailId": ticket_detail_id,
                    "serviceNumber": service_number,
                }
            ],
            "notes": [],
            "resultTypeId": work_queue_id
        }
        return await self._bruin_client.change_detail_work_queue(ticket_id, put_work_queue_payload)

    async def get_ticket_task_history(self, filters):
        ticket_current_task = await self._bruin_client.get_ticket_task_history(filters)
        if ticket_current_task["status"] in range(200, 300):
            ticket_current_task["body"] = ticket_current_task["body"]["result"]
        return ticket_current_task

    async def get_ticket_overview(self, ticket_id):
        if not ticket_id or not ticket_id.isdigit():
            return {'body': 'not ticket id found', 'status': 404}
        params = {'ticket_id': int(ticket_id)}
        self._logger.info(f'Getting ticket overview: {ticket_id} from Bruin...')
        ticket_response = await self._bruin_client.get_all_tickets(params)
        if ticket_response["status"] not in range(200, 300):
            return ticket_response
        if len(ticket_response['body']) > 0:
            ticket_response['body'] = ticket_response['body'][0]
        return ticket_response
