## Get predictions by ticket id
* for ticket in tickets:
  ```
  self._logger.info(f"Claiming T7 predictions for ticket {ticket_id}...")
  ```
  * [get_ticket_task_history](../repositories/bruin_repository/get_ticket_task_history.md)
    ```
    self._logger.warning(f"Bad status calling to get ticket history. "
                                     f"Skipping for ticket id: {ticket_id} ...")
    ```
  * If any ticket row has asset:
    ```
    self._logger.info(f"Task history of ticket {ticket_id} doesn't have any asset. Skipping...")
    ```
  * [get_prediction](../repositories/t7_repository/get_prediction.md)
    ```
    self._logger.warning(f"Bad status calling to t7 predictions. "
                                     f"Skipping predictions for ticket id: {ticket_id}")
    ```
  * If not predictions:
    ```
    self._logger.info(f"There are no predictions for ticket {ticket_id}. Skipping...")
    ```
  ```
  self._logger.info(f"T7 predictions found for ticket {ticket_id}!")
  ```