## Subject: bruin.email.tag.request

_Message arrives at subject_

* If message body doesn't have `email_id` or `tag_id`:
  ```python
  logger.error(f"Cannot add a tag to email using {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
logger.info(f'Adding tag_id "{tag_id}" to email_id "{email_id}"...')
```

[post_email_tag](../repositories/bruin_repository/post_email_tag.md)

* If status from `post_email_tag` is in range of 200 - 300:
    ```python
    logger.info(f"Tags successfully added to email_id: {email_id} ")
    ```
* Else
    ```python
    logger.error(f"Error adding tags to email: Status: {response['status']} body: {response['body']}")
    ```
    END