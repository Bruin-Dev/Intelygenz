## Get single ticket info with service numbers

[get_single_ticket_basic_info](get_single_ticket_basic_info.md)

details = [get_ticket_details](get_ticket_details.md)

* if details["status"] not in range of 200 and 300
  ```python
  log.error(f"Error while retrieving details from ticket {ticket_id}")
  ```