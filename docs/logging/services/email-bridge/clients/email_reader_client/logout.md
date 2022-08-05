## Logout

* If there is not a server connection:
  ```python
  self._logger.error(f"Cannot log out due to current email server being None")
  ```
  END

* If there is an error while trying to log out:
  ```python
  f"Cannot close connection due to {err} of type {type(err).__name__}. Proceeding to logout..."
  ```
  END

```python
self._logger.info("Logged out from Gmail!")
```