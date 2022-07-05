## Process affecting trouble Documentation

```
self._logger.info(
            f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
            f"{serial_number}"
        )
```

* [Get open affecting tickets](../repositories/bruin_repository/get_open_affecting_tickets.md)
* if open_affecting_ticket
  ```
  self._logger.info(
                f"An open Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}"
            )
  ```
  * if task_resolved
    ```
    self._logger.info(
                    f"Service Affecting ticket with ID {ticket_id} is open, but the task related to edge "
                    f"{serial_number} is Resolved. Therefore, the ticket will be considered as Resolved."
                )
    ```
  * else
    * [Append latest trouble to ticket](_append_latest_trouble_to_ticket.md)

* else no open_affecting_ticket
  ```
  self._logger.info(f"No open Service Affecting ticket was found for edge {serial_number}")
  ```

* if not trouble_processed and not resolved_affecting_ticket
  * [Get resolved affecting tickets](../repositories/bruin_repository/get_resolved_affecting_tickets.md)

* if not trouble_processed and resolved_affecting_ticket
  ```
  self._logger.info(
                f"A resolved Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}"
            )
  ```
  * [Unresolve task for affecting_ticket](_unresolve_task_for_affecting_ticket.md)

* else
  ```
  self._logger.info(f"No resolved Service Affecting ticket was found for edge {serial_number}")
  ```

* if not trouble_processed and not open_affecting_ticket and not resolved_affecting_ticket:
  ```
  self._logger.info(f"No open or resolved Service Affecting ticket was found for edge {serial_number}")
  ```
  * [Create affecting ticket](_create_affecting_ticket.md)

```
self._logger.info(
            f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
            f"{serial_number} has been processed"
        )
```
  