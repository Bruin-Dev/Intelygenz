## Upload bandwidth report to S3 after it's generated and emailed

```python
logger.info(f'[bandwidth-reports] Csv attachment {file_name} found')
logger.info(f'[bandwidth-reports] Uploading csv attachment {file_name_and_client_id} to S3')
```

_csv report is uploaded_

* If report uploaded successfully:
  ```python
  logger.info(f'[bandwidth-reports] Csv attachment {file_name_and_client_id} sent to S3')
  ```
* Otherwise:
  ```python
  logger.error(f'[bandwidth-reports] Csv attachment {file_name_and_client_id} not sent to S3')
  ```
