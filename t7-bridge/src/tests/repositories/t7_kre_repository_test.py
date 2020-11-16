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

    def save_prediction_test(self):
        predictions = [
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

        expected_predictions = [
            {
                "asset": "some_serial_number",
                "task_results": [
                    {
                        "name": "Some action",
                        "probability": 0.9484384655952454
                    },
                ]
            }
        ]

        available_options = [
            {'asset': 'VC1234567', 'available_options': ['Request Completed']},
            {'asset': 'VC9999999', 'available_options': ['Request Completed']}
        ]

        suggested_notes = [
            {'asset': 'VC1234567', 'suggested_note': 'This is TNBA note 1', 'details': None},
            {'asset': 'VC9999999', 'suggested_note': 'This is TNBA note 2', 'details': None}
        ]

        return_value = {"body": "Saved 1 prediction", "status": 200}

        logger = Mock()
        t7_kre_client = Mock()
        t7_kre_client.save_prediction = Mock(return_value=return_value)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)

        saved_prediction = t7_kre_repository.save_prediction(
            self.valid_ticket_id,
            self.valid_ticket_rows,
            predictions,
            available_options,
            suggested_notes
        )

        t7_kre_client.save_prediction.assert_called_once_with({
            "ticket_id": self.valid_ticket_id,
            "ticket_rows": self.expected_ticket_rows,
            "asset_predictions": expected_predictions,
            "asset_available_options": available_options,
            "asset_suggestions_feedback": suggested_notes
        })
        assert saved_prediction == return_value

    def save_prediction_with_errors_test(self):
        predictions = [
            {
                'assetId': 'VC05200016134',
                'error': {
                    'code': 'error_in_prediction',
                    'message': (
                        'Error executing prediction: The labels [\'Refer to ASR Carrier\']'
                        ' are not in the "Task Result" labels map.'
                    )
                }
            },
            {
                'assetId': '33.NBCB.108797',
                'error': {
                    'code': 'error_in_prediction',
                    'message': (
                        'Error executing prediction: The labels [\'Refer to ASR Carrier\']'
                        ' are not in the "Task Result" labels map.'
                    )
                }
            }
        ]

        expected_predictions = [
            {'asset': predictions[0]['assetId'], 'error': predictions[0]['error']},
            {'asset': predictions[1]['assetId'], 'error': predictions[1]['error']}
        ]

        available_options = [
            {'asset': 'VC1234567', 'available_options': ['Request Completed']},
            {'asset': 'VC9999999', 'available_options': ['Request Completed']}
        ]

        suggested_notes = [
            {'asset': 'VC1234567', 'suggested_note': None, 'details': 'detail'},
            {'asset': 'VC9999999', 'suggested_note': None, 'details': 'detail'}
        ]

        return_value = {"body": "Saved 1 prediction", "status": 200}

        logger = Mock()
        t7_kre_client = Mock()
        t7_kre_client.save_prediction = Mock(return_value=return_value)

        t7_kre_repository = T7KRERepository(logger, t7_kre_client)

        saved_prediction = t7_kre_repository.save_prediction(
            self.valid_ticket_id,
            self.valid_ticket_rows,
            predictions,
            available_options,
            suggested_notes
        )

        t7_kre_client.save_prediction.assert_called_once_with({
            "ticket_id": self.valid_ticket_id,
            "ticket_rows": self.expected_ticket_rows,
            "asset_predictions": expected_predictions,
            "asset_available_options": available_options,
            "asset_suggestions_feedback": suggested_notes
        })
        assert saved_prediction == return_value
