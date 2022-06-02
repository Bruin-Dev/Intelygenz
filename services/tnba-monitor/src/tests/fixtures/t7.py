from typing import List

import pytest
from tests.fixtures import _constants as constants


# Model-as-dict generators
def __generate_prediction(*, name: str, probability: float):
    return {
        "name": name,
        "probability": probability,
    }


# Factories
@pytest.fixture(scope="session")
def make_prediction_object():
    def _inner(*, serial_number: str, predictions: List[dict] = None):
        predictions = predictions or []

        return {
            "assetId": serial_number,
            "predictions": predictions,
        }

    return _inner


@pytest.fixture(scope="session")
def make_erroneous_prediction_object():
    def _inner(*, serial_number: str, error_msg: str = None):
        return {
            "assetId": serial_number,
            "error": {
                "code": "error_in_prediction",
                "message": error_msg,
            },
        }

    return _inner


# Predictions
@pytest.fixture(scope="session")
def holmdel_noc_prediction():
    return __generate_prediction(name=constants.HOLMDEL_NOC_PREDICTION_NAME, probability=0.5)


@pytest.fixture(scope="session")
def confident_request_completed_prediction():
    return __generate_prediction(name=constants.REQUEST_COMPLETED_PREDICTION_NAME, probability=0.90)


@pytest.fixture(scope="session")
def unconfident_request_completed_prediction():
    return __generate_prediction(name=constants.REQUEST_COMPLETED_PREDICTION_NAME, probability=0.50)


@pytest.fixture(scope="session")
def confident_repair_completed_prediction():
    return __generate_prediction(name=constants.REPAIR_COMPLETED_PREDICTION_NAME, probability=0.90)


@pytest.fixture(scope="session")
def unconfident_repair_completed_prediction():
    return __generate_prediction(name=constants.REPAIR_COMPLETED_PREDICTION_NAME, probability=0.50)


# RPC responses
@pytest.fixture(scope="session")
def t7_500_response():
    return {
        "body": "Got internal error from T7",
        "status": 500,
    }
