import os
import re

from functools import partial
from typing import List


TNBA_NOTE_PREDICTION_LINE_REGEX = re.compile(r'^The next best action for .* is: (?P<prediction_name>.*?)\.')


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
        tnba_note_lines = tnba_note['noteValue'].split(os.linesep)
        tnba_note_prediction_line = self._utils_repository.get_first_element_matching(
            tnba_note_lines,
            lambda line: TNBA_NOTE_PREDICTION_LINE_REGEX.match(line) is not None,
        )

        if not tnba_note_prediction_line:
            # Let's consider the prediction has changed if no prediction with the expected format is found in the note
            return True

        prediction_match = TNBA_NOTE_PREDICTION_LINE_REGEX.match(tnba_note_prediction_line)
        prediction_name = prediction_match.group('prediction_name')
        best_prediction_name = best_prediction['name']

        return not (prediction_name == best_prediction_name)

    @staticmethod
    def is_request_or_repair_completed_prediction(prediction: dict) -> bool:
        return prediction['name'] in ['Request Completed', 'Repair Completed']

    def is_prediction_confident_enough(self, prediction: dict) -> bool:
        return prediction['probability'] >= self._config.MONITOR_CONFIG['request_repair_completed_confidence_threshold']
