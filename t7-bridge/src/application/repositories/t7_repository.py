class T7Repository:

    def __init__(self, logger, t7_client):
        self._logger = logger
        self._t7_client = t7_client

    def get_prediction(self, ticket_id):
        return self._t7_client.get_prediction(ticket_id)
