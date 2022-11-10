## Generate and send Daily Bandwidth Report

```python
logger.info(f"[bandwidth-reports] Generating report for client {client_id}...")
```

[BruinRepository::get_affecting_ticket_for_report](../../repositories/bruin_repository/get_affecting_ticket_for_report.md)

_Report data is generated_

* If report data could be generated:
  ```python
  logger.info(f"Got {len(report_items)} rows for the report for client {client_id}")
  ```
* Otherwise:
  ```python
  logger.warning(f"Couldn't generate any rows for the report for client {client_id}")
  ```

```python
logger.info(f"Sending report of {len(report_items)} rows to client {client_id} sent via email...")
```

```python
logger.info(f"[bandwidth-reports] Report for client {client_id} sent via email")
```