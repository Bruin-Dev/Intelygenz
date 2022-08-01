from typing import List, Optional

from application.servers.grpc.email_tagger.email_tagger_pb2 import PredictionResponse, SaveMetricsResponse


def prediction_response(
    success: bool = True,
    message: str = "success",
    email_id: str = "4593892",
    predictions: Optional[List[PredictionResponse.Prediction]] = None,
):
    if predictions is None:
        predictions = [prediction()]

    return PredictionResponse(
        success=success,
        message=message,
        email_id=email_id,
        prediction=predictions,
    )


def prediction(tag_id: int = 1, probability: float = 1.0):
    return PredictionResponse.Prediction(tag_id=tag_id, probability=probability)


def save_metrics_response():
    return SaveMetricsResponse(message="success")
