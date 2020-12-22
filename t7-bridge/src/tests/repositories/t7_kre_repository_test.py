from unittest.mock import Mock

from application.repositories.t7_kre_repository import T7KRERepository


class TestT7KRERepository:
    valid_ticket_id = 123
    valid_ticket_rows = [
        {
            "Asset": "asset1",
            "CallTicketID": valid_ticket_id,
            "Initial Note @ Ticket Creation": "9/22/2020 11:45:08 AM",
            "EnteredDate_N": "2020-09-22T11:44:54.85-04:00",
            "Notes": "note 1",
            "Task Result": None,
            "Ticket Status": "Closed",
            "Address1": "address 1",
        },
        {
            "Asset": None,
            "CallTicketID": valid_ticket_id,
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
            "call_ticket_id": valid_ticket_id,
            "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
            "entered_date_n": "2020-09-22T11:44:54.85-04:00",
            "notes": "note 1",
            "task_result": None,
            "ticket_status": "Closed",
            "address1": "address 1",
        },
        {
            "asset": None,
            "call_ticket_id": valid_ticket_id,
            "initial_note_ticket_creation": "9/22/2020 11:45:08 AM",
            "entered_date_n": "2020-09-22T11:44:54.85-04:00",
            "notes": "note 2",
            "task_result": None,
            "ticket_status": "Closed",
            "address1": "address 2",
        }
    ]

    def instance_test(self):
        logger = Mock()
        t7_kre_client = Mock()

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)

        assert t7_kre_repository._logger is logger
        assert t7_kre_repository._t7_kre_client is t7_kre_client

    def get_prediction_200_test(self):
        raw_predictions = {
            "body": {
                "assetPredictions": [
                    {
                        "asset": "some_serial_number",
                        "taskResults": [
                            {
                                "name": "Some action",
                                "probability": 0.9484384655952454
                            },
                        ]
                    }
                ]
            },
            "status": 200
        }

        expected_predictions = {
            "body": [
                {
                    "assetId": "some_serial_number",
                    "predictions": [
                        {
                            "name": "Some action",
                            "probability": 0.9484384655952454
                        },
                    ]
                }
            ],
            "status": 200
        }

        logger = Mock()

        t7_kre_client = Mock()
        t7_kre_client.get_prediction = Mock(return_value=raw_predictions)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)
        predictions = t7_kre_repository.get_prediction(
            ticket_id=self.valid_ticket_id,
            ticket_rows=self.valid_ticket_rows
        )

        t7_kre_repository._t7_kre_client.get_prediction.assert_called_once_with(
            self.valid_ticket_id, self.expected_ticket_rows
        )
        assert predictions == expected_predictions

    def get_prediction_not_200_test(self):
        raw_predictions = {
            "body": "error test",
            "status": 500
        }

        logger = Mock()

        t7_kre_client = Mock()
        t7_kre_client.get_prediction = Mock(return_value=raw_predictions)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)
        predictions = t7_kre_repository.get_prediction(
            ticket_id=self.valid_ticket_id,
            ticket_rows=self.valid_ticket_rows
        )

        t7_kre_repository._t7_kre_client.get_prediction.assert_called_once_with(
            self.valid_ticket_id, self.expected_ticket_rows
        )
        assert predictions == raw_predictions

    def post_automation_metrics_test(self):
        params = {"ticket_id": self.valid_ticket_id, "ticket_rows": self.valid_ticket_rows}
        return_value = {"body": "Saved 1 metrics", "status": 200}

        logger = Mock()
        t7_kre_client = Mock()
        t7_kre_client.post_automation_metrics = Mock(return_value=return_value)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)

        post_automation_metrics = t7_kre_repository.post_automation_metrics(params)
        t7_kre_repository._t7_kre_client.post_automation_metrics.assert_called_once_with(
            self.valid_ticket_id, self.expected_ticket_rows
        )
        assert post_automation_metrics == return_value
