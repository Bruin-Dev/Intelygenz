## Subject: bruin.customer.get.info_by_did

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get Bruin client info by DID using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `did`:
  ```python
  logger.error(f'Cannot get Bruin client info by DID using {json.dumps(body)}. Need "did"') 
  ```
  END

```python
logger.info(f"Getting Bruin client info by DID with body: {json.dumps(body)}")
```

[get_client_info_by_did](../repositories/bruin_repository/get_client_info_by_did.md)

```python
logger.info(
    f"Bruin client_info_by_did published in event bus for request {json.dumps(msg)}. "
    f"Message published was {response}"
)
```
