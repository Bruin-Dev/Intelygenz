## Start monitoring

```python
self._logger.info("Scheduling Gateway Monitor job...")
```

* If job should be executed on service start:
    ```python
    self._logger.info("Gateway Monitor job is going to be executed immediately")
    ```
    [_monitoring_process](_monitoring_process.md)

* If there's a running job to monitor gateways already:
    ```python
    self._logger.info(f"Skipping start of Gateway Monitoring job. Reason: {conflict}")
    ```
