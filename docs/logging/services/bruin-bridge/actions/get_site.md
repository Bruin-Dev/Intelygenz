## Subject: bruin.get.site

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot get bruin site using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `client_id` filter:
  ```python
  self._logger.error(f'Cannot get bruin site using {json.dumps(filters)}. Need "client_id"')
  ```
  END

* If message body doesn't have `site_id` filter:
  ```python
  self._logger.error(f'Cannot get bruin site using {json.dumps(filters)}. Need "site_id"')
  ```
  END

```python
self._logger.info(f"Getting Bruin site with filters: {json.dumps(filters)}")
```

[get_site](../repositories/bruin_repository/get_site.md)

```python
self._logger.info(
    f"Bruin get_site published in event bus for request {json.dumps(msg)}. Message published was {response}"
)
```
