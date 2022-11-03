## _get_ticket_task_histories

```python
logger.info("Creating ticket map of ticket id to ticket task history")
```

* Iterate over the ticket list

```python
logger.info(f"Grabbing the ticket task history for ticket {ticket_id}")
```

* If ticket task history doesn't return 200

 END

```python
logger.info(f"Parsing all data in the ticket task history for ticket {ticket_id}")
```

* We parse tickets history and return them
