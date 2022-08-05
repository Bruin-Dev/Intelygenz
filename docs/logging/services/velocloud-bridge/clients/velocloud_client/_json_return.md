## JSON return

* If the response has errors:
    * If the response indicates that the authentication token expired:
        ```python
        logger.info(f"Response returned: {response}. Attempting to relogin")
        ```

        [_start_relogin_job](_start_relogin_job.md)

    * Otherwise:
      ```python
      logger.error(f"Error response returned: {response}")
      ```