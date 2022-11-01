## Subject: t7.prediction.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get prediction using {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`, `ticket_rows` and `assets_to_predict` filters:
  ```python
  logger.error(
                f"Cannot get prediction using {json.dumps(payload)}. "
                f'Need parameters "ticket_id", "ticket_rows" and "assets_to_predict"'
            )
  ```
  END

[get_prediction](../repositories/t7_kre_repository/get_prediction.md)

```python
logger.info(f"Prediction for ticket {ticket_id} published in event bus!")
```
