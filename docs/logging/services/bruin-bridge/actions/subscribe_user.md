## Subject: bruin.subscribe.user

_Message arrives at subject_

_Try to get Message body_

* Catch `ValidationError`:
  ```python
  self.logger.warning(f"Wrong request message: msg={msg}, validation_error={e}")
  ```
  END

```python
self.logger.info(f"Subscribing user: post_request={post_request}")
```

[post](../clients/bruin_client/post.md)

* If response.status from `post` is `HTTPStatus.UNAUTHORIZED`
  ```python
  self.logger.error(f"Got 401 from Bruin. Re-logging in...")
  ```
  END