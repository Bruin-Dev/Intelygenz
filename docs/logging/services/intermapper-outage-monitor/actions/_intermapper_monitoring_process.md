## Intermapper monitoring process
```
self._logger.info(f'Processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}')
```
* If status is not Ok:
  ```
  self._logger.warning(f"Bad status calling to get unread emails. "
                                 f"Skipping intermapper monitoring process ...")
  ```
* [_process_email_batch](_process_email_batch.md)
```
self._logger.info(
            f'Finished processing unread emails from {self._config.INTERMAPPER_CONFIG["inbox_email"]}. '
            f"Elapsed time: {round((stop - start) / 60, 2)} minutes"
        )
```