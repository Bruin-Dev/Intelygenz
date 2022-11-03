## get_digi_recovery_logs

```python
logger.info(
    f"Getting DiGi recovery logs from "
    f'{self._config.DIGI_CONFIG["days_of_digi_recovery_log"]} '
    f"day(s) ago"
)
```

* Request from nats DiGi recovery logs

```python
logger.info(
    f'Got DiGi recovery logs from {self._config.DIGI_CONFIG["days_of_digi_recovery_log"]} ' f"day(s) ago"
)
```

* If fails with an error

```python
logger.error(
    f"Error while attempting to get DiGi recovery logs in "
    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
    f"Error {response_status} - {response_body}"
)
```

END

* If the connection with the bridge fails

```python
logger.error(
    f"An error occurred when attempting to get DiGi recovery logs -> {e}"
)
```

END