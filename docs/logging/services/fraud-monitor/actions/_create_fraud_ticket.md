## Create fraud ticket

```python
logger.info(f"Creating Fraud ticket for client {client_id} and service number {service_number}")
```
* If not contacts:
  ```python
  logger.warning(f"Not found contacts to create the fraud ticket")
  ```
* If environment is not PRODUCTION:
  ```python
  logger.info(f"No Fraud ticket will be created since the current environment is not production")
  ```
* [create_fraud_ticket](../repositories/bruin_repository/create_fraud_ticket.md)
* If status is not Ok:
  ```python
  logger.warning(
      f"Bad status calling to create fraud ticket with client id: {client_id} and"
      f"service number: {service_number}. Create fraud ticket return FALSE ..."
  )
  ```
```python
logger.info(f"Fraud ticket was successfully created! Ticket ID is {ticket_id}")
```
* [append_note_to_ticket](../repositories/bruin_repository/append_note_to_ticket.md)
* If status is not Ok:
  ```python
  logger.warning(
      f"Bad status calling to append note to ticket id: {ticket_id} and service number:"
      f"{service_number}. Create fraud ticket return FALSE ..."
  )
  ```
```python
logger.info(f"Fraud note was successfully appended to ticket {ticket_id}!")
logger.info(f"Forwarding ticket {ticket_id} to HNOC")
```
* [change_detail_work_queue_to_hnoc](../repositories/bruin_repository/change_detail_work_queue_to_hnoc.md)
