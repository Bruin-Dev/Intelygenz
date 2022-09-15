## Report incident

```python
self._logger.info(
    f"Reporting {gateway['trouble'].value} incident to ServiceNow "
    f"for host {gateway['host']} and gateway {gateway['name']}..."
)
```

* If there's an exception:
    ```python
    self._logger.error(f"An error occurred when reporting incident to ServiceNow -> {e}")
    ```

* If response status is not OK:
    ```python
    self._logger.error(
      f"Failed to report {gateway['trouble'].value} incident to ServiceNow "
      f"for host {gateway['host']} and gateway {gateway['name']} in {environment} environment: "
      f"Error {response_status} - {response_body}"
    )
    ```
* Else:
    ```python
    self._logger.info(
      f"Reported {gateway['trouble'].value} incident to ServiceNow "
      f"for host {gateway['host']} and gateway {gateway['name']}!"
    )
    ```
