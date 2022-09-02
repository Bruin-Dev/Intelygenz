## Subject: request.switches.data

_Message arrives at subject_

* If message doesn't have `body`:
  ```python
  logger.error(f"Cannot get SWITCHES data with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message doesn't have filter keys in the REQUEST_MODEL:
  ```python
  logger.error(f"Cannot get SWITCHES data with {json.dumps(payload)}. Make sure it complies with the shape of {REQUEST_MODEL}"
  ```
  END

```python
logger.info(f"Getting SWITCHES data for payload {payload}...")
```

[get_switches_data](../repositories/forticloud_repository/get_switches_data.md)

```python
logger.info(f"Published SWITCHES data for payload {payload}")
```
