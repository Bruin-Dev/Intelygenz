## Subscribe consumer from the event bus to subject

```python
self._logger.info(
    f"Subscribing consumer {consumer_name} from the event bus to subject {topic} and adding it under NATS "
    f"queue {queue}..."
)
```

[subscribe_action](../../nats/clients/subscribe_action.md)

```python
self._logger.info(f"Consumer {consumer_name} from the event bus subscribed successfully")
```