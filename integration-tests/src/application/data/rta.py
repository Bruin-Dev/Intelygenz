import logging
from typing import List, Optional

from application.servers.grpc.rta.rta_pb2 import (
    OutputFilterFlags,
    PredictionResponse,
    SaveClosedTicketsFeedbackResponse,
    SaveCreatedTicketsFeedbackResponse,
    SaveOutputsResponse,
)

log = logging.getLogger(__name__)


def prediction_response(
    potential_service_numbers: Optional[List[str]] = None,
    potential_ticket_numbers: Optional[List[str]] = None,
    predicted_class: str = "",
    filter_flags: OutputFilterFlags = OutputFilterFlags(),
) -> PredictionResponse:
    if potential_service_numbers is None:
        potential_service_numbers = []
    if potential_ticket_numbers is None:
        potential_ticket_numbers = []

    return PredictionResponse(
        potential_service_numbers=potential_service_numbers,
        potential_ticket_numbers=potential_ticket_numbers,
        predicted_class=predicted_class,
        filter_flags=filter_flags,
    )


def output_filter_flags(
    tagger_is_below_threshold: bool = False,
    rta_model1_is_below_threshold: bool = False,
    rta_model2_is_below_threshold: bool = False,
    is_filtered: bool = False,
    in_validation_set: bool = False,
):
    return OutputFilterFlags(
        tagger_is_below_threshold=tagger_is_below_threshold,
        rta_model1_is_below_threshold=rta_model1_is_below_threshold,
        rta_model2_is_below_threshold=rta_model2_is_below_threshold,
        is_filtered=is_filtered,
        in_validation_set=in_validation_set,
    )


def save_outputs_response(success: bool = True) -> SaveOutputsResponse:
    return SaveOutputsResponse(success=success)


def save_created_ticket_feedback_response(success: bool = True) -> SaveCreatedTicketsFeedbackResponse:
    return SaveCreatedTicketsFeedbackResponse(success=success)


def save_closed_ticket_feedback_response(success: bool = True) -> SaveClosedTicketsFeedbackResponse:
    return SaveClosedTicketsFeedbackResponse(success=success)
