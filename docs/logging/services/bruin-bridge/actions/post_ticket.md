## Subject: bruin.ticket.creation.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot create a ticket using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `clientId`, `category`, `services`, `contacts`:
  ```python
  logger.info(
                f"Cannot create ticket using {json.dumps(payload)}. "
                f'Need "clientId", "category", "services", "contacts"'
            )
  ```
  END

```python
logger.info(f'Creating ticket for client id: {payload["clientId"]}...')
```

[post_ticket](../repositories/bruin_repository/post_ticket.md)

* If status from `post_ticket` is in range 200 - 300:
    ```python
    logger.info(
                f'Ticket created for client id: {payload["clientId"]} with ticket id:'
                f' {result["body"]["ticketIds"][0]}'
            )
    ```
* Else
  ```python
  logger.error(response["body"])
  ```
  END