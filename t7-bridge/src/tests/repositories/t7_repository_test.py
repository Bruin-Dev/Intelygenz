from unittest.mock import Mock

from application.repositories.t7_repository import T7Repository


class TestT7Repository:

    def instance_test(self):
        logger = Mock()
        t7_client = Mock()

        t7_repository = T7Repository(logger, t7_client)

        assert t7_repository._logger is logger
        assert t7_repository._t7_client is t7_client

    def get_prediction_test(self):
        ticket_id = 123
        ticket_rows = [
            {
                "Asset": "asset1",
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 1",
                "Task Result": None,
                "Ticket Status": "Closed",
                "Address1": "address 1",
            },
            {
                "Asset": None,
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 2",
                "Task Result": None,
                "Ticket Status": "Closed",
                "Address1": "address 2",
            }
        ]

        expected_ticket_rows = [
            {
                "asset": "asset1",
                "call_ticket_id": ticket_id,
                "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
                "entered_date_n": "2020-09-22T11:44:54.85-04:00",
                "notes": "note 1",
                "task_result": None,
                "ticket_status": "Closed",
                "address1": "address 1",
            },
            {
                "asset": None,
                "call_ticket_id": ticket_id,
                "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
                "entered_date_n": "2020-09-22T11:44:54.85-04:00",
                "notes": "note 2",
                "task_result": None,
                "ticket_status": "Closed",
                "address1": "address 2",
            }
        ]
        assets = [
            {
                "assetId": "some_serial_number",
                "predictions": [
                    {
                        "name": "Some action",
                        "probability": 0.9484384655952454
                    },
                ]
            }
        ]

        raw_predictions = {
            "body": {
                "assets": assets,
                "requestId": "e676150a-73b9-412b-8207-ac2a3bbc9cbc"
            },
            "status": 200
        }

        expected_predictions = {
            "body": assets,
            "status": 200
        }

        logger = Mock()

        t7_client = Mock()
        t7_client.get_prediction = Mock(return_value=raw_predictions)

        t7_repository = T7Repository(logger, t7_client)
        predictions = t7_repository.get_prediction(ticket_id=ticket_id, ticket_rows=ticket_rows)

        t7_repository._t7_client.get_prediction.assert_called_once_with(ticket_id, expected_ticket_rows)
        assert predictions == expected_predictions

    def get_prediction_not_200_test(self):
        ticket_id = 123
        ticket_rows = [
            {
                "Asset": "asset1",
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 1",
                "Task Result": None,
                "Ticket Status": "Closed",
                "Address1": "address 1",
                "SLA": "sla1",
            },
            {
                "Asset": None,
                "CallTicketID": ticket_id,
                "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
                "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
                "Notes": "note 2",
                "Task Result": None,
                "Ticket Status": "Closed",
                "Address1": "address 2",
                "SLA": "sla2",
            }
        ]

        expected_ticket_rows = [
            {
                "asset": "asset1",
                "call_ticket_id": ticket_id,
                "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
                "entered_date_n": "2020-09-22T11:44:54.85-04:00",
                "notes": "note 1",
                "task_result": None,
                "ticket_status": "Closed",
                "address1": "address 1",
                "sla": "sla1",
            },
            {
                "asset": None,
                "call_ticket_id": ticket_id,
                "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
                "entered_date_n": "2020-09-22T11:44:54.85-04:00",
                "notes": "note 2",
                "task_result": None,
                "ticket_status": "Closed",
                "address1": "address 2",
                "sla": "sla2",
            }
        ]
        raw_predictions = {
            "body": "Got internal error from Bruin",
            "status": 500
        }

        logger = Mock()

        t7_client = Mock()
        t7_client.get_prediction = Mock(return_value=raw_predictions)

        t7_repository = T7Repository(logger, t7_client)
        predictions = t7_repository.get_prediction(ticket_id=ticket_id, ticket_rows=ticket_rows)

        t7_repository._t7_client.get_prediction.assert_called_once_with(ticket_id, expected_ticket_rows)
        assert predictions == raw_predictions

    def post_automation_metrics_test(self):
        params = {"ticket_id": 123, "ticket_rows": []}
        return_value = {"body": "No content", "status": 204}

        logger = Mock()
        t7_client = Mock()
        t7_client.post_automation_metrics = Mock(return_value=return_value)

        t7_repository = T7Repository(logger, t7_client)

        post_automation_metrics = t7_repository.post_automation_metrics(params)
        assert post_automation_metrics == return_value
