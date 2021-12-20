import pytest
from typing import Any, Dict, List


@pytest.fixture(scope='session')
def make_filter_flags():
    def _inner(
            *,
            tagger_is_below_threshold: bool = False,
            rta_model1_is_below_threshold: bool = False,
            rta_model2_is_below_threshold: bool = False,
            in_validation_set: bool = False,
            is_filtered: bool = False,
    ):
        return {
            "tagger_threshold_value": 0.95,
            "tagger_is_below_threshold": tagger_is_below_threshold,
            "rta_model1_threshold_value": 0.95,
            "rta_model1_is_below_threshold": rta_model1_is_below_threshold,
            "rta_model2_threshold_value": 0.95,
            "rta_model2_is_below_threshold": rta_model2_is_below_threshold,
            "is_filtered": is_filtered,
            "filtered_reason": "belongs_to_mailbox_003",
            "is_validation_set": in_validation_set,
            "validation_set_probability": 0.3,
        }

    return _inner


@pytest.fixture(scope='session')
def make_classification():
    def _inner(
            *,
            predicted_class: str = 'VOO',
    ):
        return {
            "predicted_class": predicted_class,
            "predicted_class_voovas_vs_other": "VOO/VAS",
            "predicted_class_voovas_vs_other_probability": 0.7,
            "predicted_class_voo_vs_vas": "VOO",
            "predicted_class_voo_vs_vas_probability": 0.8,
        }

    return _inner


@pytest.fixture(scope='session')
def make_inference_data(make_filter_flags, make_classification):
    def _inner(
            *,
            potential_service_numbers: List[str] = None,
            filter_flags: Dict[str, Any] = None,
            classification: Dict[str, Any] = None,
    ):
        filter_flags = filter_flags or make_filter_flags()
        classification = classification or make_classification()
        return {
            "potential_service_numbers": potential_service_numbers,
            "classification": classification,
            "filter_flags": filter_flags
        }

    return _inner
