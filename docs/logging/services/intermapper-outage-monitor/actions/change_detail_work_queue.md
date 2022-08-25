## Change detail work queue

[change_detail_work_queue](../repositories/bruin_repository/change_detail_work_queue.md)

* If response status for change detail work queue is ok:
    ```python
    logger.info(
        f"Successfully forwarded ticket_id {ticket_id} and serial {serial_number} to {target_queue} queue."
    )
    ```
    * If target queue is `HNOC Investigate`:
        * [send_forward_email_milestone_notification](../repositories/bruin_repository/send_forward_email_milestone_notification.md)
        * If response for send forward email milestone notification is not ok:
          ```python
          logger.error(
              f"Forward email related to service number {serial_number} could not be sent for ticket "
              f"{ticket_id}!"
          )
          ```
* Otherwise:
  ```python
  logger.error(
      f"Failed to forward ticket_id {ticket_id} and "
      f"serial {serial_number} to {target_queue} queue due to bruin "
      f"returning {change_detail_work_queue_response} when attempting to forward to {target_queue} queue."
  )
  ```