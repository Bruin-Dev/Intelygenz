## Search messages

Search unread messages with the given constraints

* If there is an error while connecting to the email server:
  ```python
  self._logger.error(f"Unable to access the unread mails due to {err}")
  ```
  END

* If it fails to get any emails:
  ```python
  self._logger.error(f"Unable to access the unread mails")
  ```
  END

```python
self._logger.info(f"Search resp code: {search_resp_code}. Number of unseen messages: {len(messages)}")
```

```python
self._logger.info(f"Messages to process in next batch: {messages}")
```
