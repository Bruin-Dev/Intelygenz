## Login

  [create connection](create_connection.md)

* If failed to create server connection:
  ```python
  logger.error(f"There was an error trying to create the connection to the inbox: {err}")
  ```
  END

Call Email Server login endpoint using authentication credentials.

* If there is an error while trying to open the inbox:
  ```python
  logger.error(f"Unable to open the {recipient_folder} folder")
  ```
  END

* If there is an error while trying to log in to the inbox:
  ```python
  logger.error(f"There was an error trying to login into the inbox: {err}")
  ```
  END

```python
logger.info(f"Logged in to Gmail mailbox!")
```
