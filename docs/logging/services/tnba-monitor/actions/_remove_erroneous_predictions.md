## Remove erroneous predictions
* for ticket in prediction tickets:
  * for prediction in predictions:
    * If error in prediction:
      ```
      self._logger.info(
                        f"Prediction for serial {serial_number} in ticket {ticket_id} was found but it contains an "
                        f"error from T7 API -> {prediction_obj['error']}"
                    )
      ```
    
  * If not valid prediction:
    ```
    self._logger.info(f"All predictions in ticket {ticket_id} were erroneous. Skipping ticket...")
    ```