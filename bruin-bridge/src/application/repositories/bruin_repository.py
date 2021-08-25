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

    async def get_tickets_basic_info(self, params: dict, ticket_statuses: List[str]) -> dict:
        tasks = []
        for ticket_status in ticket_statuses:
            payload = {
                **params.copy(),
                'ticket_status': ticket_status,
            }

            get_ticket_task = self._bruin_client.get_tickets_basic_info(payload)
            tasks.append(get_ticket_task)

        tickets_responses = await asyncio.gather(*tasks)
        tickets = [
            ticket_response['body']['responses']
            for ticket_response in tickets_responses
            if ticket_response['status'] in range(200, 300)
        ]
        tickets = sum(tickets, [])

        return {
            'body': tickets,
            'status': 200,
        }

    async def get_single_ticket_basic_info(self, ticket_id: int) -> dict:
        payload = {
            'TicketID': ticket_id
        }
        ticket_response = await self._bruin_client.get_tickets_basic_info(payload)

        if ticket_response['status'] not in range(200, 300):
            return ticket_response

        ticket_list = ticket_response['body']['responses']

        if len(ticket_list) == 0:
            self._logger.error(f'Call to get_tickets_basic_info succeeded, but TicketID {ticket_id} not found.')
            return {
                'body': {},
                'status': 404
            }

        return {
            'body': ticket_list[0],
            'status': ticket_response['status'],
        }

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

    async def unpause_ticket(self, ticket_id, serial_number, detail_id):
        filters = {}
        if serial_number:
            filters['serviceNumber'] = serial_number
        if detail_id:
            filters['DetailId'] = detail_id
        return await self._bruin_client.unpause_ticket(ticket_id, filters)

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
        is_bruin_custom_status = status_code in (409, 471, 472, 473)
        if not (status_code in range(200, 300) or is_bruin_custom_status):
            return response

        response['body'] = response['body']['ticketId']
        return response

    async def get_client_info(self, filters):
        response = await self._bruin_client.get_client_info(filters)

        if response["status"] not in range(200, 300):
            return response

        documents = response["body"].get("documents")
        response_body = []
        if documents:
            active_status = [status for status in documents if
                             status["status"] == "A" and status["serviceNumber"] in filters["service_number"]]
            for status in active_status:
                response_body.append({"client_id": status.get("clientID"),
                                      "client_name": status.get("clientName")})

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
        get_work_queues_filters = {}
        put_work_queues_filters = {}

        if "detail_id" in filters:
            ticket_detail_id = filters["detail_id"]
            get_work_queues_filters['DetailId'] = ticket_detail_id
            put_work_queues_filters['detailId'] = ticket_detail_id
        if "service_number" in filters:
            service_number = filters["service_number"]
            get_work_queues_filters['ServiceNumber'] = service_number
            put_work_queues_filters['serviceNumber'] = service_number
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
        queue_name = filters["queue_name"]
        current_task_name = possible_work_queues_response_body['currentTaskName']
        if current_task_name is not None and current_task_name.strip() == queue_name:
            return {
                'body': f'Ticket {ticket_id} is already in the queue {queue_name}',
                'status': 400,
            }
        if not work_queues:
            return {
                'body': f'No work queues were found for ticket {ticket_id} and filters {get_work_queues_filters}',
                'status': 404,
            }

        work_queue_id = None
        for possible_work_queue in work_queues:
            result_name = possible_work_queue["resultName"]
            if result_name is not None and result_name.strip() == queue_name:
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
                put_work_queues_filters
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
        if not ticket_id or (isinstance(ticket_id, str) and not ticket_id.isdigit()):
            return {'body': 'not ticket id found', 'status': 404}
        params = {'ticket_id': int(ticket_id)}
        self._logger.info(f'Getting ticket overview: {ticket_id} from Bruin...')
        ticket_response = await self._bruin_client.get_all_tickets(params)
        if ticket_response["status"] not in range(200, 300):
            return ticket_response
        if len(ticket_response['body']) > 0:
            ticket_response['body'] = ticket_response['body'][0]
        return ticket_response

    async def get_circuit_id(self, params):
        return await self._bruin_client.get_circuit_id(params)

    async def post_email_tag(self, email_id: str, tag_id: str):
        return await self._bruin_client.post_email_tag(email_id, tag_id)

    async def change_ticket_severity(self, ticket_id: int, payload: dict):
        payload = {
            'Severity': payload['severity'],
            'Reason': payload['reason'],
        }

        return await self._bruin_client.change_ticket_severity(ticket_id, payload)

    async def get_site(self, params):
        response = await self._bruin_client.get_site(params)

        if response["status"] not in range(200, 300):
            return response

        documents = response["body"].get("documents", [])
        response_body = documents

        response["body"] = response_body
        return response
