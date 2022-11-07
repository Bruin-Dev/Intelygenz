## Run old email reprocessing polling

```python
log.info("Starting ReprocessOldParentEmails process...")

log.info(f"Found {len(list(old_parent_emails))} old parent emails")

log.info(f"Found {len(old_parent_emails_filtered)} old parent emails to be discarded")
```

* for old_parent_email in old_parent_emails
  [_prepare_email_to_reprocess](_prepare_email_to_reprocess.md)