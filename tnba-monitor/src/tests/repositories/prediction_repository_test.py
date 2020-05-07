import os

from application.repositories.prediction_repository import PredictionRepository
from application.repositories.utils_repository import UtilsRepository


class TestPredictionRepository:
    def find_predictions_by_serial_test(self):
        serial_number = 'VC1234567'

        prediction_1 = {
            'assetId': serial_number,
            'predictions': [
                {
                    'name': 'Repair Completed',
                    'probability': 0.9484384655952454
                },
                {
                    'name': 'Holmdel NOC Investigate',
                    'probability': 0.1234567890123456
                },
            ]
        }
        prediction_2 = {
            'assetId': 'VC9999999',
            'predictions': [
                {
                    'name': 'Request Completed',
                    'probability': 0.1111111111111111
                },
                {
                    'name': 'No Trouble Found - Carrier Issue',
                    'probability': 0.2222222222222222
                },
            ]
        }
        predictions = [
            prediction_1,
            prediction_2,
        ]

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.find_prediction_object_by_serial(predictions, serial_number)
        assert result == prediction_1

    def get_best_prediction_test(self):
        prediction_1 = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }
        prediction_2 = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }
        predictions = [
            prediction_1,
            prediction_2,
        ]

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.get_best_prediction(predictions)
        assert result == prediction_1

    def is_best_prediction_different_from_prediction_in_tnba_note_with_no_prediction_found_in_note_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The note was written with a wrong format just to test this edge case',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        best_prediction = {
            'name': 'Repair Completed',
            'probability': 0.9484384655952454
        }

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, best_prediction)

        assert result is True

    def is_best_prediction_different_from_prediction_in_tnba_note_with_no_changes_in_predictions_names_or_probs_test(
            self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The ticket next best action should be Holmdel NOC Investigate. Confidence: 94.8438 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        best_prediction = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.9484384655952454
        }

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, best_prediction)

        assert result is False

    def are_predictions_different_from_predictions_in_tnba_note_with_changes_in_predictions_names_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The ticket next best action should be Holmdel NOC Investigate. Confidence: 94.8438 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        best_prediction = {
            'name': 'Wireless Repair Intervention Needed',
            'probability': 0.9484384655952454
        }

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, best_prediction)

        assert result is True

    def are_predictions_different_from_predictions_in_tnba_note_with_changes_in_predictions_probabilities_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The ticket next best action should be Holmdel NOC Investigate. Confidence: 94.8438 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        best_prediction = {
            'name': 'Holmdel NOC Investigate',
            'probability': 0.1234567890123456
        }

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, best_prediction)

        assert result is True

    def are_predictions_different_from_predictions_in_tnba_note_with_changes_in_predictions_names_and_probs_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The ticket next best action should be Holmdel NOC Investigate. Confidence: 94.8438 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        best_prediction = {
            'name': 'Wireless Repair Intervention Needed',
            'probability': 0.9999999999999999
        }

        utils_repository = UtilsRepository()

        prediction_repository = PredictionRepository(utils_repository)

        result = prediction_repository.is_best_prediction_different_from_prediction_in_tnba_note(
            tnba_note, best_prediction)

        assert result is True
