## Process Service Affecting trouble

```python
logger.info(
    f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
    f"{serial_number}"
)
```

[BruinRepository::get_open_affecting_tickets](../../repositories/bruin_repository/get_open_affecting_tickets.md)

* If response status of get open affecting tickets is not ok:
  ```python
  logger.error(
      f"Error while getting open Service Affecting tickets for edge {serial_number}: "
      f"{open_affecting_tickets_response}. Skipping processing Service Affecting trouble..."
  )
  ```
  END

[_get_oldest_affecting_ticket_for_serial_number](_get_oldest_affecting_ticket_for_serial_number.md)

* If the oldest open Service Affecting ticket and its details could be found:
  ```python
  logger.info(f"An open Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}")
  ```

  * If the task related to the link's edge under a Service Affecting trouble is resolved:
    ```python
    logger.info(
        f"Service Affecting ticket with ID {ticket_id} is open, but the task related to edge "
        f"{serial_number} is Resolved. Therefore, the ticket will be considered as Resolved."
    )
    ```

    [...]

    ```python
    logger.info(
        f"A resolved Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}"
    )
    ```

    [_unresolve_task_for_affecting_ticket](_unresolve_task_for_affecting_ticket.md)

    [...]

    ```python
    logger.info(
        f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
        f"{serial_number} has been processed"
    ) 
    ```

    END

  * Otherwise:

    [_append_latest_trouble_to_ticket](_append_latest_trouble_to_ticket.md)

    * If ticket task should NOT be forwarded to HNOC:

        [_send_reminder](_send_reminder.md)

    [...]

    ```python
    logger.info(
        f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
        f"{serial_number} has been processed"
    ) 
    ```

    END

```python
logger.info(f"No open Service Affecting ticket was found for edge {serial_number}")
```

[BruinRepository::get_resolved_affecting_tickets](../../repositories/bruin_repository/get_resolved_affecting_tickets.md)

[_get_oldest_affecting_ticket_for_serial_number](_get_oldest_affecting_ticket_for_serial_number.md)

* If the oldest resolved Service Affecting ticket and its details could be found:
    ```python
    logger.info(
        f"A resolved Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}"
    )
    ```

    [_unresolve_task_for_affecting_ticket](_unresolve_task_for_affecting_ticket.md)

    [...]

    ```python
    logger.info(
        f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
        f"{serial_number} has been processed"
    ) 
    ```

    END

```python
logger.info(f"No resolved Service Affecting ticket was found for edge {serial_number}")
```

```python
logger.info(f"No open or resolved Service Affecting ticket was found for edge {serial_number}")
```

[_create_affecting_ticket](_create_affecting_ticket.md)

```python
logger.info(
    f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
    f"{serial_number} has been processed"
) 
```

  