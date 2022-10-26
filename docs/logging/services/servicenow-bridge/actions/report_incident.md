## Subject: servicenow.incident.report.request

_Message arrives at subject_

* If message doesn't have `body`:
  ```python
  log.error(f"Cannot report incident with {json.dumps(payload)}. Must include body in request")
  ```
  END

* If message body doesn't have `host`, `gateway`, `summary`, `note` and `link` filters:
  ```python
  log.error(f"Cannot report incident using {json.dumps(payload)}. JSON malformed")
  ```
  END

[report_incident](../repositories/servicenow_repository/servicenow_repository.md)

```python
log.info(f"Report incident response: {response}")
```