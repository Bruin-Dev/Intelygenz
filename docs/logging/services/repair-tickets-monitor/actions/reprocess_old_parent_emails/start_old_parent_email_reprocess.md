## Start old parent email reprocess

```python
log.info("Scheduling Reprocess Old Parent Emails job...")
```

* if exec_on_start
    ```python
    log.info("ReprocessOldParentEmails job is going to be executed immediately")
    ```


* try
   [_run_old_email_reprocessing_polling](_run_old_email_reprocessing_polling.md)

* catch `ConflictingIdError`
  ```python
  log.info(f"Skipping start of ReprocessOldParentEmails job. Reason: {conflict}")
  ```