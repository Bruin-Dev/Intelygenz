import pytest
from application.repositories.prediction_repository import PredictionRepository


class TestPredictionRepository:
    def find_predictions_by_serial_test(
        self, prediction_repository, make_prediction_object, serial_number_1, serial_number_2, holmdel_noc_prediction
    ):
        prediction_object_1 = make_prediction_object(
            serial_number=serial_number_1,
            predictions=[holmdel_noc_prediction],
        )
        prediction_object_2 = make_prediction_object(
            serial_number=serial_number_2,
            predictions=[holmdel_noc_prediction],
        )
        prediction_objects = [
            prediction_object_1,
            prediction_object_2,
        ]

        result = prediction_repository.find_prediction_object_by_serial(prediction_objects, serial_number_1)
        assert result == prediction_object_1

    def filter_predictions_in_next_results_test(
        self,
        make_next_result_item,
        holmdel_noc_prediction,
        confident_request_completed_prediction,
        confident_repair_completed_prediction,
    ):
        predictions = [
            confident_repair_completed_prediction,
            holmdel_noc_prediction,
            confident_request_completed_prediction,
        ]

        next_result_request_completed = make_next_result_item(result_name="Request Completed")
        next_result_holmdel_noc = make_next_result_item(result_name="Holmdel NOC Investigate ")
        next_results_list = [
            next_result_request_completed,
            next_result_holmdel_noc,
        ]

        result = PredictionRepository.filter_predictions_in_next_results(predictions, next_results_list)
        expected = [
            holmdel_noc_prediction,
            confident_request_completed_prediction,
        ]
        assert result == expected

    @pytest.mark.parametrize(
        "predictions",
        [
            (
                [
                    {"name": "Repair Completed", "probability": 0.9484384655952454},
                    {"name": "Holmdel NOC Investigate", "probability": 0.1234567890123456},
                    {"name": "Request Completed", "probability": 0.1111111111111111},
                ]
            ),
            (
                [
                    {"name": "Repair Completed", "probability": 0.9484384655952454},
                    {"name": "Holmdel NOC Investigate", "probability": 0.1234567890123456},
                ]
            ),
        ],
        ids=["get_max_value", "add_other_value"],
    )
    def map_request_and_repair_completed_predictions_test(self, predictions):
        result = PredictionRepository.map_request_and_repair_completed_predictions(predictions)

        assert result == [
            {"name": "Repair Completed", "probability": 0.9484384655952454},
            {"name": "Holmdel NOC Investigate", "probability": 0.1234567890123456},
            {"name": "Request Completed", "probability": 0.9484384655952454},
        ]

    def get_best_prediction_test(
        self, prediction_repository, confident_request_completed_prediction, unconfident_request_completed_prediction
    ):
        predictions = [
            unconfident_request_completed_prediction,
            confident_request_completed_prediction,
        ]

        result = prediction_repository.get_best_prediction(predictions)
        assert result == confident_request_completed_prediction

    def is_best_prediction_different_from_prediction_in_tnba_note_with_no_changes_in_prediction_name_test(
        self, prediction_repository, make_standard_tnba_note, serial_number_1, holmdel_noc_prediction
    ):
        prediction_name = holmdel_noc_prediction["name"]
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1, prediction_name=prediction_name)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, holmdel_noc_prediction
        )
        assert result is False

    def is_best_prediction_different_from_prediction_in_AI_autoresolve_tnba_note_with_no_changes_in_prediction_test(
        self,
        prediction_repository,
        make_AI_autoresolve_tnba_note,
        serial_number_1,
        confident_request_completed_prediction,
    ):
        tnba_note = make_AI_autoresolve_tnba_note(serial_number=serial_number_1)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, confident_request_completed_prediction
        )
        assert result is False

    def is_best_prediction_different_from_prediction_in_tnba_note_with_changes_in_prediction_name_test(
        self, prediction_repository, make_standard_tnba_note, serial_number_1, holmdel_noc_prediction
    ):
        prediction_name = "No Trouble Found"
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1, prediction_name=prediction_name)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, holmdel_noc_prediction
        )
        assert result is True

    def is_best_prediction_different_from_prediction_in_AI_autoresolve_tnba_note_with_changes_in_prediction_name_test(
        self, prediction_repository, make_AI_autoresolve_tnba_note, serial_number_1, holmdel_noc_prediction
    ):
        tnba_note = make_AI_autoresolve_tnba_note(serial_number=serial_number_1)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, holmdel_noc_prediction
        )
        assert result is True

    def is_request_or_repair_completed_prediction_test(
        self, holmdel_noc_prediction, confident_request_completed_prediction, confident_repair_completed_prediction
    ):
        result = PredictionRepository.is_request_or_repair_completed_prediction(confident_request_completed_prediction)
        assert result is True

        result = PredictionRepository.is_request_or_repair_completed_prediction(confident_repair_completed_prediction)
        assert result is True

        result = PredictionRepository.is_request_or_repair_completed_prediction(holmdel_noc_prediction)
        assert result is False

    def is_prediction_confident_enough_test(
        self, prediction_repository, confident_request_completed_prediction, unconfident_repair_completed_prediction
    ):
        result = prediction_repository.is_prediction_confident_enough(unconfident_repair_completed_prediction)
        assert result is False

        result = prediction_repository.is_prediction_confident_enough(confident_request_completed_prediction)
        assert result is True
