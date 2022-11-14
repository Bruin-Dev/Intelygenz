## Schedule re-check job for edges in the quarantine

```python
logger.info(f"Scheduling recheck job for {len(edges)} edges in {outage_type.value} state...")
```

_[_recheck_edges_for_ticket_creation](_recheck_edges_for_ticket_creation.md) is scheduled for execution after some time_

```python
logger.info(f"Edges in {outage_type.value} state scheduled for recheck successfully")
```