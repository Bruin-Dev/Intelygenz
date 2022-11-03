## _merge_recovery_logs

```python
logger.info("Merging recovery logs data into ticket map")
logger.info(
    f"Merging data from DiGi recovery logs of ticket id {ticket_id} "
    "into the ticket ID to ticket task history map"
)
```

* We take all the recovery logs data and fill in the other values of each dictionary in the ticket map respectively based
on matching ticket ids.
