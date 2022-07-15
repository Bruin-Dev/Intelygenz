## Intermapper monitoring process

```python
self._logger.info(f'Processing all unread email from {self._config.INTERMAPPER_CONFIG["inbox_email"]}')
```

[get_unread_emails](../repositories/notifications_repository/get_unread_emails.md)

* If response status of getting unread emails is not ok:
  ```python
  self._logger.warning(f"Bad status calling to get unread emails. Skipping intermapper monitoring process...")
  ```
  END

* Group e-mails by Circuit ID in batches.

* For every batch of e-mails:
    * [_process_email_batch](_process_email_batch.md)

```python
self._logger.info(
    f'Finished processing unread emails from {self._config.INTERMAPPER_CONFIG["inbox_email"]}. '
    f"Elapsed time: {round((stop - start) / 60, 2)} minutes"
)
```