## Process device
```
self._logger.info(f"Processing device {serial_number}...")
```
* for test result in test results:
  * If test result passed:
    * [_process_passed_test_result](_process_passed_test_result.md)
  * If test result failed:
    * [_process_failed_test_result](_process_failed_test_result.md)
  * Else: 
    ```
    self._logger.info(
                    f'Test result {test_result["summary"]["id"]} has state {test_result["summary"]["status"].upper()}. '
                    "Skipping..."
                )
    ```
* [_append_new_notes_for_device](_append_new_notes_for_device.md)
```
self._logger.info(f"Finished processing device {serial_number}!")
```