## Subject: hawkeye.test.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get probe's tests using {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `probe_uids` filter:
  ```python
  logger.error(
     f"Cannot get probe's tests using {json.dumps(body)}. "
     f"Must include 'probe_uids' in the body of the request"
  )
  ```
  END

* If message body doesn't have `interval` filter:
  ```python
  logger.error(
     f"Cannot get probe's tests using {json.dumps(body)}. "
     f"Must include 'interval' in the body of the request"
  )
  ```
  END

```python
logger.info(
    f"Collecting all test results with filters: "
    f"{json.dumps(body['probe_uids'])} {json.dumps(body['interval'])}..."
)
```

[get_test_results](../repositories/hawkeye_repository/get_test_results.md)
