## Save outputs


```python
log.info(
            "request_id=%s email_id=%s Sending data to save output in repair-tickets-kre-bridge",
            request_id,
            output.email_id,
        )
```
* try 
  response = event_bus.request
* catch `Exception`
  ```python
  log.error(
                "request_id=%s email_id=%s "
                "Exception occurred when getting inference from repair-tickets-kre-bridge: %s"
                % (request_id, output.email_id, exception)
            )
  ```
* if response["status"] does not equal 200
  ```python
  log.error(
              "request_id=%s email_id=%s "
              "Bad response code received from repair-tickets-kre-bridge: %s - %s"
              % (
                  request_id,
                  output.email_id,
                  response_status,
                  response_body,
              )
          )
  ```
```python
log.info("request_id=%s email_id=%s Output saved", request_id, output.email_id)
```