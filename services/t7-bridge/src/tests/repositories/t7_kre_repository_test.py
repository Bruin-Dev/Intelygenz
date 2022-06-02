from unittest.mock import Mock, patch

from application.repositories.t7_kre_repository import T7KRERepository


class TestT7KRERepository:
    valid_ticket_id = 123
    valid_assets_to_predict = ["asset1"]
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
        },
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
        },
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
                "asset_predictions": [
                    {
                        "asset": "some_serial_number",
                        "task_results": [
                            {"name": "Some action", "probability": 0.9484384655952454},
                        ],
                    }
                ]
            },
            "status": 200,
        }

        expected_predictions = {
            "body": [
                {
                    "assetId": "some_serial_number",
                    "predictions": [
                        {"name": "Some action", "probability": 0.9484384655952454},
                    ],
                }
            ],
            "status": 200,
        }

        logger = Mock()

        t7_kre_client = Mock()
        t7_kre_client.get_prediction = Mock(return_value=raw_predictions)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)
        predictions = t7_kre_repository.get_prediction(
            ticket_id=self.valid_ticket_id,
            ticket_rows=self.valid_ticket_rows,
            assets_to_predict=self.valid_assets_to_predict,
        )

        t7_kre_repository._t7_kre_client.get_prediction.assert_called_once_with(
            self.valid_ticket_id, self.expected_ticket_rows, self.valid_assets_to_predict
        )
        assert predictions == expected_predictions

    def get_prediction_not_200_from_client_test(self):
        expected_response = {"body": "Error from get_prediction client", "status": 500}

        logger = Mock()

        t7_kre_client = Mock()
        t7_kre_client.get_prediction = Mock(return_value=expected_response)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)
        response = t7_kre_repository.get_prediction(
            ticket_id=self.valid_ticket_id,
            ticket_rows=self.valid_ticket_rows,
            assets_to_predict=self.valid_assets_to_predict,
        )

        t7_kre_repository._t7_kre_client.get_prediction.assert_called_once_with(
            self.valid_ticket_id, self.expected_ticket_rows, self.valid_assets_to_predict
        )
        assert response == expected_response

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

    def post_live_automation_metrics_test(self):
        valid_ticket_id = 99999999
        valid_asset_id = "VC0000000"
        automated_successfully = False

        return_value = {"body": "Metric saved successfully", "status": 200}

        logger = Mock()
        t7_kre_client = Mock()
        t7_kre_client.post_live_automation_metrics = Mock(return_value=return_value)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)

        post_automation_metrics = t7_kre_repository.post_live_automation_metrics(
            ticket_id=valid_ticket_id, asset_id=valid_asset_id, automated_successfully=automated_successfully
        )
        t7_kre_repository._t7_kre_client.post_live_automation_metrics.assert_called_once_with(
            valid_ticket_id, valid_asset_id, automated_successfully
        )
        assert post_automation_metrics == return_value
