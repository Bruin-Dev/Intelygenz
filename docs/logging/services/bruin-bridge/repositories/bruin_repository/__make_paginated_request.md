## Make paginated request to Bruin API

```python
self._logger.info(f"Fetching all pages using {fn.__name__}...")
```
  
* While there are pages to fetch:
    * Make a call for the current page to Bruin API through the BruinClient
    * If response status is not ok:
      ```python
      self._logger.warning(
          f"Call to {fn.__name__} failed for page {current_page}. Checking if max retries threshold has been "
          "reached"
      )
      ```

        * If the max attempts threshold hasn't been reached:
          ```python
          self._logger.info(
              f"Max retries threshold hasn't been reached yet. Retrying call to {fn.__name__} for page "
              f"{current_page}..."
          )
          ```
        * Otherwise:
          ```python
          self._logger.error(f"There have been {max_retries} or more errors when calling {fn.__name__}.")
          ```
          END
  
    * If there are no more pages to fetch:
      ```python
      self._logger.info(f"Finished fetching all pages for {fn.__name__}.")
      ```
      END