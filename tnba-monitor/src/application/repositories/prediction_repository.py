import os
import re

from functools import partial
from typing import List


TNBA_NOTE_PREDICTION_LINE_REGEX = re.compile(
    r'^\d{1,2}\) (?P<prediction_name>\w+(\s\w+)*) \| '
    r'Confidence: (?P<prediction_probability>(100\.0)|(\d|[1-9]\d)\.\d{1,14}) %$'
)


class PredictionRepository:
    def __init__(self, utils_repository):
        self._utils_repository = utils_repository

    @staticmethod
    def __prediction_belongs_to_serial(prediction: dict, serial_number: str) -> bool:
        return prediction['assetId'] == serial_number

    def find_prediction_object_by_serial(self, predictions: List[dict], serial_number: str) -> dict:
        prediction_lookup_fn = partial(self.__prediction_belongs_to_serial, serial_number=serial_number)
        return self._utils_repository.get_first_element_matching(predictions, prediction_lookup_fn)

    @staticmethod
    def are_predictions_different_from_predictions_in_tnba_note(tnba_note: dict, predictions: List[dict]) -> bool:
        tnba_note_predictions: List[dict] = []

        tnba_note_lines = tnba_note['noteValue'].split(os.linesep)
        for line in tnba_note_lines:
            prediction_match = TNBA_NOTE_PREDICTION_LINE_REGEX.match(line)
            if prediction_match:
                prediction_name = prediction_match.group('prediction_name')
                prediction_probability = round(float(prediction_match.group('prediction_probability')) / 100, 16)

                prediction = {
                    'name': prediction_name,
                    'probability': prediction_probability,
                }
                tnba_note_predictions.append(prediction)

        return not (predictions == tnba_note_predictions)
