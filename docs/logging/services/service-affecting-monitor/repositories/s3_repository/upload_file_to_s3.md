## Upload File to S3

* If there's an error while uploading the file to S3:
  ```python
  logger.exception(f"Error: S3 upload failed {e}")
  ```