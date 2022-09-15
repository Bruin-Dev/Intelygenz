## Monitoring process

```python
self._logger.info(f"Starting Gateway Monitoring process...")
```

* For each VeloCloud host:
    * [_process_host](_process_host.md)
    * If there's an exception:
        ```python
        self._logger.exception(e)
        ```

```python
self._logger.info(f"Gateway Monitoring process finished! Elapsed time: {round((stop - start) / 60, 2)} minutes")
```
