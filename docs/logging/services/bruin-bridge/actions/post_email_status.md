## Subject: bruin.email.status

_Message arrives at subject_

_Try to use `parse_obj` on Message body_

* `ValidationError` caught:
  ```python
  self.logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
  ```
  END


```python
self.logger.info(f"Setting email status: post_request={post_request}")
```

[post](../clients/bruin_client/post.md)

* if response.status from calling `post` is `HTTPStatus.UNAUTHORIZED`
  ```python
  self.logger.error(f"Got 401 from Bruin. Re-logging in...")
  ```
  END
