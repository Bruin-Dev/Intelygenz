## Mark as read

  [login](login.md)

* If there is an error while connecting to the email server:
  ```python
  logger.error(f"Cannot mark email {msg_uid} as read due to email server being None")
  ```
  END
  
Mark email related to the given identifier `msg_uid` as read

* If there is an error while marking the email as read:
  ```python
  logger.error(f"Error marking message {msg_uid} as read due to {err}")
  ```
  END

  [logout](logout.md)
