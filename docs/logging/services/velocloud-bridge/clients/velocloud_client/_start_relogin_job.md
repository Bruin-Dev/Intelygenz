## Start relogin job

```python
logger.info(f"Scheduling relogin job for host {host}...")
```

[_relogin_client](_relogin_client.md) is scheduled to trigger immediately

* If there's a relogin job already scheduled for that VeloCloud host:
  ```python
  logger.error(f"Skipping start of relogin job for host {host}. Reason: {conflict}")
  ```
  END

```python
logger.info(f"Relogin job for host {host} has been scheduled")
```