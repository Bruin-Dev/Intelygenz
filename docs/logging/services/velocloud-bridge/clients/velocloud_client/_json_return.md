## JSON return

* If the response has errors:
    * If the response indicates that the authentication token expired:
        ```python
        logger.info(f"Response returned: {response}. Logging in...")
        ```

        [_login](_login.md)

    * Otherwise:
      ```python
      logger.error(f"Error response returned: {response}")
      ```