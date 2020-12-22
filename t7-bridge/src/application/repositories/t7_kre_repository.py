import re
import humps
from typing import List


class T7KRERepository:

    def __init__(self, logger, t7_kre_client):
        self._logger = logger
        self._t7_kre_client = t7_kre_client

    def get_prediction(self, ticket_id: int, ticket_rows: List[dict]) -> dict:
        camel_ticket_rows = list(map(
            self.__row_dict_to_camel,
            ticket_rows
        ))

        prediction = self._t7_kre_client.get_prediction(ticket_id, camel_ticket_rows)

        if prediction["status"] in range(200, 300):
            predictions = prediction["body"]["asset_predictions"]
            body_prediction_response = list(
                map(
                    lambda p: {
                        "assetId": p["asset"],
                        "predictions": p["task_results"]
                    } if "task_results" in p else {
                        "assetId": p["asset"],
                        "error": p["error"]
                    },
                    predictions
                )
            )
            prediction["body"] = body_prediction_response
        else:
            return prediction

        return prediction

    def post_automation_metrics(self, params: dict) -> dict:
        ticket_id = params['ticket_id']
        camel_ticket_rows = list(map(
            self.__row_dict_to_camel,
            params['ticket_rows']
        ))

        post_metrics_response = self._t7_kre_client.post_automation_metrics(ticket_id, camel_ticket_rows)
        return post_metrics_response

    @staticmethod
    def __row_dict_to_camel(row_input):
        row_output = {}
        for key in row_input:
            formatted_key = re.sub(r'[\W_]+', '', key)
            formatted_key = humps.decamelize(formatted_key)
            formatted_key = formatted_key.lower()
            row_output[formatted_key] = row_input[key]
        return row_output
