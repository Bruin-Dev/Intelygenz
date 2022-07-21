## Execute action for message

```python
self._logger.info(f'Message received from topic {msg_subject}')
```

* If there is no action for target subject:
  ```python
  self._logger.error(f'No ActionWrapper defined for topic {msg_subject}.')
  ```
  END

Execute action for subject

* If execution failed:
  ```python
  self._logger.exception(
      "NATS Client Exception in client happened. "
      f"Error executing action {self._topic_action[msg_subject].target_function} "
      f"from {type(self._topic_action[msg_subject].state_instance).__name__} instance."
  )
  ```