## Make paginated request to Hawkeye API

```python
logger.info(f"Check all pages")
logger.info(f"Fetching all pages using {fn.__name__}...")
```
  
* While there are pages to fetch:
    * Make a call for the current page to Hawkeye API through the HawkeyeClient
    * If response status is not ok:
      ```python
      logger.warning(f"Call to {fn.__name__} failed. Checking if max retries threshold has been reached")
      ```

        * If the max attempts threshold has been reached:
          ```python
           logger.error(f"There have been 5 or more errors when calling {fn.__name__}. ")
          ```
          END
  
    * If there are no more pages to fetch:
      ```python
      logger.info(f"Finished fetching all pages for {fn.__name__}.")
      ```
      END