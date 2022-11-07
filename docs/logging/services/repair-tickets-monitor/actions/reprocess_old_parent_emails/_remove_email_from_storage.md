## Remove email from storage

_Delete email from repair parent email storage_

* if deleting the parent email returns 0
  ```python
  log.error(f"Error while removing old parent email with id {old_parent_email.id} from storage")
  ```