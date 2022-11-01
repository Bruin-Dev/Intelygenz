## Subject: t7.automation.metrics

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot post automation metrics using {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`, and `ticket_rows` filters:
  ```python
  logger.error(
                f"Cannot post automation metrics using {json.dumps(payload)}. "
                f'Need parameter "ticket_id" and "ticket_rows"'
            )
  ```
  END

[post_automation_metrics](../repositories/t7_kre_repository/post_automation_metrics.md)

```python
logger.info(f'Metrics posted for ticket {payload["ticket_id"]} published in event bus!')
```
