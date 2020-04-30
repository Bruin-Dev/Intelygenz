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

    def are_predictions_different_from_predictions_in_tnba_note_with_no_changes_in_predictions_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The following are the next best actions for this ticket with corresponding confidence levels:',
                '1) Repair Completed | Confidence: 94.84384655952454 %',
                '2) Holmdel NOC Investigate | Confidence: 12.34567890123456 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        predictions = [
            {
                'name': 'Repair Completed',
                'probability': 0.9484384655952454
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]

        result = PredictionRepository.are_predictions_different_from_predictions_in_tnba_note(tnba_note, predictions)

        assert result is False

    def are_predictions_different_from_predictions_in_tnba_note_with_changes_in_predictions_names_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The following are the next best actions for this ticket with corresponding confidence levels:',
                '1) Repair Completed | Confidence: 94.84384655952454 %',
                '2) Holmdel NOC Investigate | Confidence: 12.34567890123456 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        predictions = [
            {
                'name': 'Wireless Repair Intervention Needed',
                'probability': 0.9484384655952454
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]

        result = PredictionRepository.are_predictions_different_from_predictions_in_tnba_note(tnba_note, predictions)

        assert result is True

    def are_predictions_different_from_predictions_in_tnba_note_with_changes_in_predictions_probabilities_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The following are the next best actions for this ticket with corresponding confidence levels:',
                '1) Repair Completed | Confidence: 94.84384655952454 %',
                '2) Holmdel NOC Investigate | Confidence: 12.34567890123456 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        predictions = [
            {
                'name': 'Repair Completed',
                'probability': 0.9999999999999999
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]

        result = PredictionRepository.are_predictions_different_from_predictions_in_tnba_note(tnba_note, predictions)

        assert result is True

    def are_predictions_different_from_predictions_in_tnba_note_with_changes_in_predictions_names_and_probs_test(self):
        tnba_note = {
            "noteId": 41894040,
            "noteValue": os.linesep.join([
                '#*Automation Engine*#,'
                'TNBA',
                '',
                'The following are the next best actions for this ticket with corresponding confidence levels:',
                '1) Repair Completed | Confidence: 94.84384655952454 %',
                '2) Holmdel NOC Investigate | Confidence: 12.34567890123456 %',
            ]),
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }

        predictions = [
            {
                'name': 'Wireless Repair Intervention Needed',
                'probability': 0.9999999999999999
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]

        result = PredictionRepository.are_predictions_different_from_predictions_in_tnba_note(tnba_note, predictions)

        assert result is True
