## Get single ticket basic info

```python
log.info("request_id=%s ticket_id=%s Getting ticket basic info", request_id, ticket_id)
```

* try
    response = event_bus.request

* catch `Exception`
    ```python
    log.error("request_id=%s ticket_id=%s Exception occurred when getting basic info from Bruin: %s" % (
                    request_id,
                    ticket_id,
                    exception,
                ))
    ```

* if response["status"] not equal 200
    ```python
    log.error("request_id=%s ticket_id=%s Bad response code received from Bruin bridge: %s - %s" % (
                    request_id,
                    ticket_id,
                    response_status,
                    response_body,
                ))
    ```

```python
log.info("request_id=%s ticket_id=%s Basic info for ticket retrieved from Bruin", request_id, ticket_id)
```