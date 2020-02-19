from shortuuid import uuid


class PredictionRepository:

    def __init__(self, config, logger, event_bus):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus

    async def get_prediction(self, ticket_id, serial_number):
        best_prediction = None
        prediction_request = {
            "request_id": uuid(),
            "ticket_id": ticket_id
        }
        prediction = await self._event_bus.rpc_request("t7.prediction.request", prediction_request, timeout=60)

        if prediction["status"] == 200:
            assets = prediction["prediction"]
            for asset in assets:
                asset_serial = asset.get('assetId')
                # If there is an error, there is no predictions field but status code is still 200 from them
                # Service affecting tickets normally have that problem
                predictions = asset.get('predictions')
                if predictions and asset_serial in serial_number:
                    return await self._get_best_automatable(predictions)

        return best_prediction

    async def _get_best_automatable(self, predictions):
        best_prediction = {"name": "", "probability": 0.00}
        # probability % and name, gets an array
        automatable_tasks = self._config.CONDITIONS["automatable_task_list"]
        min_probability_threshold = self._config.CONDITIONS["min_probability_threshold"]
        for prediction in predictions:
            if prediction["name"] in automatable_tasks and prediction["probability"] > min_probability_threshold:
                if best_prediction["probability"] < prediction["probability"]:
                    best_prediction = prediction

        if best_prediction["name"] == "":
            return None

        return best_prediction["name"]
