## Change detail work queue to hnoc
* [change_detail_work_queue](../../repositories/bruin_repository/change_detail_work_queue.md)
* If change detail work queue status is ok:
  ```
  self._logger.info(f"Ticket {ticket_id} and serial {serial_number} task result changed to  {task_result}")
  ```
* Else:
  ```
  self._logger.error(
                f"Failed to forward ticket_id {ticket_id} and "
                f"serial {serial_number} to {target_queue} due to bruin "
                f"returning {change_detail_work_queue_response} when attempting to forward to HNOC."
            )
  ```