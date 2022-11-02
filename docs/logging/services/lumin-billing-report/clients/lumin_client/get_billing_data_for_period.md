## Get billing data for a specific time frame

Make a call to endpoint `POST /api/billing`.

* If there is an error while connecting to the LuminAI API after multiple retries:
  ```python
  msg = "Could not connect to {} with headers {}, body {}".format(self.config["uri"], self.headers, d)
  logger.exception(msg)
  ```
