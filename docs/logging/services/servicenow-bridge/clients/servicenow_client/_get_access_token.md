## Get API access token

```python
log.info("Getting ServiceNow access token...")
```

Make a call to `POST /oauth_token.do` using the set of credentials provided.

* If there's an error while making the call to the ServiceNow API:
  ```python
  log.exception(e)
  ```
  END

* If the status of the HTTP response is `401`:
  ```python
  log.error("Failed to get a ServiceNow access token")
  ```
  END

  ```python
  log.info("Got ServiceNow access token!")
  ```