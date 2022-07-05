## Process ticket detail

```
self._logger.info(
                f"Processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}..."
            )
```

* If is a tnba note and tnba note is not old enough:
  ```
  self._logger.info(
  f"TNBA note found for ticket {ticket_id} and detail {ticket_detail_id} is too recent. "
  f"Skipping detail..."
  )
  ```
* [get_next_results_for_ticket_detail](../repositories/bruin_repository/get_next_results_for_ticket_detail.md)
* If get next result for ticket detail status is not ok:
  ```
  self._logger.warning(f"Bad status calling get next result for ticket details."
                                     f"Skipping process ticket details for ticket id: {ticket_id} and"
                                     f"ticket detail id: {ticket_detail_id}")
  ```
```
self._logger.info(
                f"Filtering predictions available in next results for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}..."
            )
```
* If not relevant predictions:
  ```
  self._logger.info(f"No predictions with name appearing in the next results were found for ticket {ticket_id}, "
                    f"detail {ticket_detail_id} and serial {serial_number}!")
  ```
```
self._logger.info(
                f"Predictions available in next results found for ticket {ticket_id}, detail {ticket_detail_id} "
                f"and serial {serial_number}: {relevant_predictions}"
            )
```
* If newest note:
  * If best prediction different that the ticket note:
    ```
    self._logger.info(
     f"Best prediction for ticket {ticket_id}, detail {ticket_detail_id} and serial {serial_number} "
                        f"didn't change since the last TNBA note was appended. Skipping detail..."
    )
    ```
```
self._logger.info(
                f"Building TNBA note from prediction {best_prediction['name']} for ticket {ticket_id}, "
                f"detail {ticket_detail_id} and serial {serial_number}..."
            )
```
* If request or repair completed prediction:
  ```
  self._logger.info(
                    f"Best prediction found for serial {serial_number} of ticket {ticket_id} is "
                    f'{best_prediction["name"]}. Running autoresolve...'
                )
  ```
  * [_autoresolve_ticket_detail](_autoresolve_ticket_detail.md)
  * If autoresolve status is SUCCES:
    * [post_live_automation_metrics](../repositories/t7_repository/post_live_automation_metrics.md)
  * If autoresolve status is SKIPPED:
    ```
    self._logger.info(
                        f"Autoresolve was triggered because the best prediction found for serial {serial_number} of "
                        f'ticket {ticket_id} was {best_prediction["name"]}, but the process failed. A TNBA note with '
                        "this prediction will be built and appended to the ticket later on."
                    )
    ```
  * IF autoresolve status is BAD_PREDICTION:
    * [post_live_automation_metrics](../repositories/t7_repository/post_live_automation_metrics.md)
    ```
    self._logger.info(
                        f"The prediction for serial {serial_number} of ticket {ticket_id} is considered wrong."
                    )
    ```
* If not TNBA note:
  ```
  self._logger.info(f"No TNBA note will be appended for serial {serial_number} of ticket {ticket_id}.")
  ```
* If environment DEV:
  ```
  self._logger.info(f"TNBA note would have been appended to ticket {ticket_id} and detail {ticket_detail_id} "
                    f"(serial: {serial_number}). Note: {tnba_note}. Details at app.bruin.com/t/{ticket_id}")
  ```
```
self._logger.info(
                f"Finished processing detail {ticket_detail_id} (serial: {serial_number}) of ticket {ticket_id}!"
            )
```