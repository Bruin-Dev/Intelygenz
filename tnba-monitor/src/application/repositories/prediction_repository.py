import re

from functools import partial
from typing import List


TNBA_NOTE_STANDARD_PREDICTION_OLD_WORDING = r'The next best action for .+ is: (?P<prediction_name>.+)\.'
TNBA_NOTE_STANDARD_PREDICTION_NEW_WORDING = (
    r"MetTel's IPA AI indicates that the next best action for .+ is: (?P<prediction_name2>.+)\."
)
TNBA_NOTE_STANDARD_PREDICTION_REGEX = re.compile(
    f'{TNBA_NOTE_STANDARD_PREDICTION_OLD_WORDING}|{TNBA_NOTE_STANDARD_PREDICTION_NEW_WORDING}',
)

TNBA_NOTE_REQUEST_REPAIR_PREDICTION_OLD_WORDING = (
    r'The next best action for .+ is: .+\. Since it is a high confidence prediction\n'
    r'the task has been automatically transitioned\.'
)
TNBA_NOTE_REQUEST_REPAIR_PREDICTION_NEW_WORDING = r"MetTel's IPA AI is resolving the task for .+\."
TNBA_NOTE_REQUEST_REPAIR_PREDICTION_REGEX = re.compile(
    f'{TNBA_NOTE_REQUEST_REPAIR_PREDICTION_OLD_WORDING}|{TNBA_NOTE_REQUEST_REPAIR_PREDICTION_NEW_WORDING}',
)


class PredictionRepository:
    def __init__(self, config, utils_repository):
        self._config = config
        self._utils_repository = utils_repository

    @staticmethod
    def __prediction_belongs_to_serial(prediction: dict, serial_number: str) -> bool:
        return prediction['assetId'] == serial_number

    def find_prediction_object_by_serial(self, predictions: List[dict], serial_number: str) -> dict:
        prediction_lookup_fn = partial(self.__prediction_belongs_to_serial, serial_number=serial_number)
        return self._utils_repository.get_first_element_matching(predictions, prediction_lookup_fn)

    @staticmethod
    def map_request_and_repair_completed_predictions(predictions: List[dict]) -> List[dict]:
        predictions_copy = predictions.copy()

        repair_completed_idx, repair_completed = next(
            ((i, prediction) for i, prediction in enumerate(predictions) if prediction['name'] == 'Repair Completed'),
            (None, None)
        )
        request_completed_idx, request_completed = next(
            ((i, prediction) for i, prediction in enumerate(predictions) if prediction['name'] == 'Request Completed'),
            (None, None)
        )

        if repair_completed and request_completed:
            if repair_completed['probability'] > request_completed['probability']:
                predictions_copy[request_completed_idx]['probability'] = repair_completed['probability']
            else:
                predictions_copy[repair_completed_idx]['probability'] = request_completed['probability']
        elif repair_completed:
            predictions_copy.append({
                'name': 'Request Completed',
                'probability': repair_completed['probability']
            })
        elif request_completed:
            predictions_copy.append({
                'name': 'Repair Completed',
                'probability': request_completed['probability']
            })

        return predictions_copy

    @staticmethod
    def filter_predictions_in_next_results(predictions: List[dict], next_results: List[dict]) -> List[dict]:
        next_results_names: List[str] = [result['resultName'].strip() for result in next_results]
        return [
            prediction
            for prediction in predictions
            if prediction['name'] in next_results_names
        ]

    def get_best_prediction(self, predictions: List[dict]) -> dict:
        highest_probability = max(prediction['probability'] for prediction in predictions)

        return self._utils_repository.get_first_element_matching(
            predictions,
            lambda action: action['probability'] == highest_probability
        )

    def is_best_prediction_different_from_prediction_in_tnba_note(self, tnba_note: dict, best_prediction: dict) -> bool:
        tnba_note_text = tnba_note['noteValue']

        request_repair_prediction_match = TNBA_NOTE_REQUEST_REPAIR_PREDICTION_REGEX.search(tnba_note_text)
        if request_repair_prediction_match:
            return not self.is_request_or_repair_completed_prediction(best_prediction)

        standard_prediction_match = TNBA_NOTE_STANDARD_PREDICTION_REGEX.search(tnba_note_text)
        if standard_prediction_match:
            prediction_name = standard_prediction_match.group('prediction_name') or \
                              standard_prediction_match.group('prediction_name2')

            best_prediction_name = best_prediction['name']
            return not (prediction_name == best_prediction_name)

    @staticmethod
    def is_request_or_repair_completed_prediction(prediction: dict) -> bool:
        return prediction['name'] in ['Request Completed', 'Repair Completed']

    def is_prediction_confident_enough(self, prediction: dict) -> bool:
        return prediction['probability'] >= self._config.MONITOR_CONFIG['request_repair_completed_confidence_threshold']
