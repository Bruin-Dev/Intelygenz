## Prepare email to reprocess

* try
  ```python
  log.info(f"Discarding {old_parent_email.id} old parent email")
  ```
  [_remove_email_from_storage](_remove_email_from_storage.md)

* catch RpcError 
  ```python
  log.error(f"Error while while marking email as new for email Id {old_parent_email.id}: {e}")
  ```
