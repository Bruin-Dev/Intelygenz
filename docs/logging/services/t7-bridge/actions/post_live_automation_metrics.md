## Subject: t7.live.automation.metrics

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot post live automation metrics using {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`, `asset_id` and `automated_successfully` filters:
  ```python
  logger.error(
                f"Cannot post live automation metrics using {json.dumps(payload)}. "
                f'Need parameters "ticket_id", "asset_id" and "automated_successfully"'
            )
  ```
  END

[post_live_automation_metrics](../repositories/t7_kre_repository/post_live_automation_metrics.md)

```python
logger.info(f"Live metrics posted for ticket {ticket_id} published in event bus!")
```
