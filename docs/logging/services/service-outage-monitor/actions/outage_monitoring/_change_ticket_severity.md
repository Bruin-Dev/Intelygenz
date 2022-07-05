## Change ticket severity

```
self._logger.info(f"[{outage_type.value}] Attempting outage ticket creation for serial {serial_number}...")
```

* If is a faulty edge:
  ```
  self._logger.info(f"Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue "
                f"is that edge {serial_number} is offline.")
  ```
    * [change_ticket_severity_for_offline_edge](../../repositories/bruin_repository/change_ticket_severity_for_offline_edge.md)
* Else:
    * If check ticket tasks
        * [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
        * If response status is not OK:
          ```
          self._logger.warning(f"Bad response calling get ticket details for ticket id: {ticket_id}. "
                            f"The ticket severity don't change")
          ```
        * If ticket have multiple unresolved task
          ```
          self._logger.info(f"Severity level of ticket {ticket_id} will remain the same, as the root cause of the outage "
                            f"issue is that at least one link of edge {serial_number} is disconnected, and this ticket "
                            f"has multiple unresolved tasks.")
          ```
  ```
  self._logger.info(f"Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue "
                    f"is that at least one link of edge {serial_number} is disconnected, and this ticket has a single "
                    "unresolved task.")
  ```
* [get_ticket_details](../../repositories/bruin_repository/get_ticket.md)
  ```
  self._logger.warning(
                f"Bad response calling get ticket for ticket id: {ticket_id}. The ticket severity don't change!")
  ```
* If ticket already in severity level:
  ```
  self._logger.info(
                f"Ticket {ticket_id} is already in severity level {target_severity}, so there is no need "
                "to change it.")
  ```
* If change severity task response is not ok
  ```
  self._logger.info(
                f"Bad response for change severity task. The ticket severity don't change")
  ```
```
  self._logger.info(
                f"Finished changing severity level of ticket {ticket_id} to {target_severity}!"
                )
  ```