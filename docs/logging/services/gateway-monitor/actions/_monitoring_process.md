## Monitoring process

```python
logger.info(f"Starting Gateway Monitoring process...")
```

* For each VeloCloud host:

    [_process_host](_process_host.md)

    * If there's an exception:
        ```python
        logger.exception(e)
        ```

```python
logger.info(f"Gateway Monitoring process finished! Elapsed time: {round((stop - start) / 60, 2)} minutes")
```
