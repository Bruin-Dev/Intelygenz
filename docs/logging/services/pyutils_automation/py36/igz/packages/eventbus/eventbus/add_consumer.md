## Add consumer to event bus

```python
self._logger.info(f"Adding consumer {consumer_name} to the event bus...")
```

* If consumer has been added to the event bus already:
  ```python
  self._logger.error(f'Consumer name {consumer_name} already registered. Skipping...')
  ```
  END

```python
self._logger.info(f"Consumer {consumer_name} added to the event bus")
```