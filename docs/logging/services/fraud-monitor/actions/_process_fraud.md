## Process fraud
* [get_client_info_by_did](../repositories/bruin_repository/get_client_info_by_did.md)
* If status not Ok:
  ```
  self._logger.warning(f"Failed to get client info by DID {did}, using default client info")
  ```
* [get_open_fraud_tickets](../repositories/bruin_repository/get_open_fraud_tickets.md)
  ```
  self._logger.warning(f"fBad status calling to get open fraud tickets for client id: {client_id} and "
                                 f"service number: {service_number}. Process fraud FALSE ...")
  ```
* [_get_oldest_fraud_ticket](_get_oldest_fraud_ticket.md) 
* If open fraud ticket:
  ```
  self._logger.info(f"An open Fraud ticket was found for {service_number}. Ticket ID: {ticket_id}")
  ```
  * If is a task resolved:
    ```
    self._logger.info(
                    f"Fraud ticket with ID {ticket_id} is open, but the task related to {service_number} is resolved. "
                    f"Therefore, the ticket will be considered as Resolved."
                )
    ```
  * Else:
    * [_append_note_to_ticket](_append_note_to_ticket.md)
* Else:
  ```
  self._logger.info(f"No open Fraud ticket was found for {service_number}") 
  ```
  * [get_resolved_fraud_tickets](../repositories/bruin_repository/get_resolved_fraud_tickets.md)
  * If status is not Ok:
    ```
    self._logger.warning(f"bad status calling to get resolved fraud tickets for client id: {client_id} "
                                     f"and service number: {service_number}. Skipping process fraud ...")
    ```
    * [_get_oldest_fraud_ticket](_get_oldest_fraud_ticket.md)
* If resolved fraud ticket:
  ```
  self._logger.info(f"A resolved Fraud ticket was found for {service_number}. Ticket ID: {ticket_id}")
  ```
  * [_unresolve_task_for_ticket](_unresolve_task_for_ticket.md)
```
self._logger.info(f"No open or resolved Fraud ticket was found for {service_number}")
```
* [_create_fraud_ticket](_create_fraud_ticket.md)