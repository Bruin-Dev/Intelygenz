class T7Repository:

    def __init__(self, logger, t7_client):
        self._logger = logger
        self._t7_client = t7_client

    def get_prediction(self, ticket_id):
        prediction = self._t7_client.get_prediction(ticket_id)
        if prediction["status"] not in range(200, 300):
            return prediction
        prediction["body"] = prediction["body"]["assets"]
        return prediction
