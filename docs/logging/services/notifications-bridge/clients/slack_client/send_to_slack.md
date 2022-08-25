## Send to slack
  
Call Slack API endpoint webhook with the set of desired query parameters.

* If there is an error while connecting to Slack API:
  ```python
  logger.error(f"post(send_to_slack) => ClientConnectionError: {e}")
  ```
  END

* If there is an unexpected error:
  ```python
  logger.error(f"post(send_to_slack) => UnexpectedError: {e}")
  ```
  END

* If the status of the HTTP response is `200`:
  ```python
  logger.info(response)
  ```
  END

* If the status of the HTTP response is other:
  ```python
  logger.warning(f"post(send_to_slack) => response={response}")
  ```
  END

