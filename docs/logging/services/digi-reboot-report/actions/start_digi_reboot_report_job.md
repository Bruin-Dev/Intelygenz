## Schedule DiGi Reboot Report job
```python
logger.info(
    "Scheduled task: DiGi reboot report process configured to run every "
    f"{self._config.DIGI_CONFIG['digi_reboot_report_time']/60} hours"
)
```

* If job should be executed on service start:
  ```python
  logger.info(f"It will be executed now")
  ```

[_digi_reboot_report_process](_digi_reboot_report_process.md)
