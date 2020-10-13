import re
import humps


class T7Repository:

    def __init__(self, logger, t7_client):
        self._logger = logger
        self._t7_client = t7_client

    def get_prediction(self, ticket_id, ticket_rows):
        camel_ticket_rows = list(map(
            self.__row_dict_to_camel,
            ticket_rows
        ))

        prediction = self._t7_client.get_prediction(ticket_id, camel_ticket_rows)
        if prediction["status"] not in range(200, 300):
            return prediction
        prediction["body"] = prediction["body"]["assets"]
        return prediction

    def post_automation_metrics(self, params):
        camel_ticket_rows = list(map(
            self.__row_dict_to_camel,
            params['ticket_rows']
        ))
        params["camel_ticket_rows"] = camel_ticket_rows
        post_metrics_response = self._t7_client.post_automation_metrics(params)
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
