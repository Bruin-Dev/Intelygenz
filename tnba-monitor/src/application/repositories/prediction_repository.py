import os
import re

from functools import partial
from typing import List


TNBA_NOTE_PREDICTION_LINE_REGEX = re.compile(r'^The ticket next best action should be (?P<prediction_name>\w+(\s\w+)*)')


class PredictionRepository:
    def __init__(self, utils_repository):
        self._utils_repository = utils_repository

    @staticmethod
    def __prediction_belongs_to_serial(prediction: dict, serial_number: str) -> bool:
        return prediction['assetId'] == serial_number

    def find_prediction_object_by_serial(self, predictions: List[dict], serial_number: str) -> dict:
        prediction_lookup_fn = partial(self.__prediction_belongs_to_serial, serial_number=serial_number)
        return self._utils_repository.get_first_element_matching(predictions, prediction_lookup_fn)

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
            # If no prediction with the expected format is found in the note, let's consider the prediction "changed"
            return True

        prediction_match = TNBA_NOTE_PREDICTION_LINE_REGEX.match(tnba_note_prediction_line)
        prediction_name = prediction_match.group('prediction_name')
        best_prediction_name = best_prediction['name']

        return not (prediction_name == best_prediction_name)
