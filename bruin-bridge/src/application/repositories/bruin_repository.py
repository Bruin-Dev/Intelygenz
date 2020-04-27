import asyncio


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
        status_ticket_list = self._bruin_client.get_all_tickets(params)
        response['status'] = status_ticket_list['status']
        if status_ticket_list["status"] not in range(200, 300):
            response['body'] = status_ticket_list['body']
            raise Exception()

        return status_ticket_list["body"]

    def get_ticket_details(self, ticket_id):
        return self._bruin_client.get_ticket_details(ticket_id)

    async def get_ticket_details_by_edge_serial(self, edge_serial, params, ticket_statuses):
        response = dict.fromkeys(["body", "status"])

        response['body'] = []
        response['status'] = 200

        filtered_tickets = await self.get_all_filtered_tickets(params=params, ticket_status=ticket_statuses,)

        if filtered_tickets['status'] not in range(200, 300):
            return filtered_tickets

        futures = [
            self._search_ticket_details_for_serial(edge_serial, ticket, response)
            for ticket in filtered_tickets['body']
        ]
        results = await asyncio.gather(*futures)

        tickets = sum(results, [])

        response['body'] = tickets

        return response

    async def _search_ticket_details_for_serial(self, edge_serial, ticket, response):
        results = []
        ticket_id = ticket['ticketID']
        ticket_details_dict = self.get_ticket_details(ticket_id)

        ticket_details_response_status = ticket_details_dict['status']
        if ticket_details_response_status not in range(200, 300):
            return []

        response['status'] = ticket_details_response_status
        ticket_details_items = ticket_details_dict["body"]['ticketDetails']

        ticket_details_items_as_booleans = map(
            lambda ticket_detail: ticket_detail['detailValue'] == edge_serial,
            ticket_details_items,
        )
        if any(ticket_details_items_as_booleans):
            results.append({
                'ticketID': ticket_id,
                **ticket_details_dict["body"],
            })
        return results

    async def get_affecting_ticket_details_by_edge_serial(self, edge_serial, client_id,
                                                          category='SD-WAN', ticket_statuses=None):
        params = {}

        if ticket_statuses is None:
            ticket_statuses = ['New', 'InProgress', 'Draft']

        params['ticket_topic'] = 'VAS'
        params['category'] = category
        params["client_id"] = client_id

        ticket_details_list = await self.get_ticket_details_by_edge_serial(
            edge_serial=edge_serial, params=params, ticket_statuses=ticket_statuses,
        )

        return ticket_details_list

    async def get_outage_ticket_details_by_edge_serial(self, edge_serial, client_id,
                                                       category='SD-WAN', ticket_statuses=None):
        params = {}

        if ticket_statuses is None:
            ticket_statuses = ['New', 'InProgress', 'Draft']

        params['ticket_topic'] = 'VOO'
        params['category'] = category
        params["client_id"] = client_id

        ticket_details_list = await self.get_ticket_details_by_edge_serial(edge_serial=edge_serial, params=params,
                                                                           ticket_statuses=ticket_statuses)

        if len(ticket_details_list['body']) > 0 and ticket_details_list['status'] in range(200, 300):
            body = ticket_details_list['body'][0]
            ticket_details_list['body'] = body

        return ticket_details_list

    def post_ticket_note(self, ticket_id, note):
        payload = {"note": note}
        return self._bruin_client.post_ticket_note(ticket_id, payload)

    def post_ticket(self, payload):
        return self._bruin_client.post_ticket(payload)

    def open_ticket(self, ticket_id, detail_id):
        payload = {"Status": "O"}
        return self._bruin_client.update_ticket_status(ticket_id, detail_id, payload)

    def resolve_ticket(self, ticket_id, detail_id):
        payload = {"Status": "R"}
        return self._bruin_client.update_ticket_status(ticket_id, detail_id, payload)

    def get_management_status(self, filters):
        response = self._bruin_client.get_management_status(filters)

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

    def post_outage_ticket(self, client_id, service_number):
        response = self._bruin_client.post_outage_ticket(client_id, service_number)

        status_code = response['status_code']
        if not (status_code in range(200, 300) or status_code == 409 or status_code == 471):
            return response

        response['body'] = response['body']['ticketId']
        return response

    def get_client_info(self, filters):
        response = self._bruin_client.get_client_info(filters)

        if response["status_code"] not in range(200, 300):
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

    def change_detail_work_queue(self, ticket_id, filters):
        service_number = filters["service_number"]
        ticket_detail_id = filters["detail_id"]

        get_work_queues_filters = {
            "ServiceNumber": service_number,
            "DetailId": ticket_detail_id,
        }

        possible_work_queues_response = self._bruin_client.get_possible_detail_next_result(
            ticket_id, get_work_queues_filters
        )
        possible_work_queues_response_body = possible_work_queues_response['body']
        possible_work_queues_response_status = possible_work_queues_response['status_code']
        if possible_work_queues_response_status not in range(200, 300):
            return {
                'body': f'Error while claiming possible work queues for ticket {ticket_id} and filters '
                        f'{get_work_queues_filters}: {possible_work_queues_response_body}',
                'status_code': possible_work_queues_response_status,
            }

        work_queues = possible_work_queues_response_body['nextResults']
        if not work_queues:
            return {
                'body': f'No work queues were found for ticket {ticket_id} and filters {get_work_queues_filters}',
                'status_code': 404,
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
                "status_code": 404
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
        return self._bruin_client.change_detail_work_queue(ticket_id, put_work_queue_payload)
