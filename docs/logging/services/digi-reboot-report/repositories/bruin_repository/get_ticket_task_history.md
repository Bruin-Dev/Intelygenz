## Get ticket task history

```python
logger.info(f"Getting ticket task history for app.bruin.com/t/{ticket_id}")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when requesting ticket task_history from Bruin API for ticket {ticket_id} "
      f"-> {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got task_history of ticket {ticket_id} from Bruin!")
```

* If response status for get management status for edge is not ok:
  ```python
  err_msg = (
      f"Error while retrieving task history of ticket {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```