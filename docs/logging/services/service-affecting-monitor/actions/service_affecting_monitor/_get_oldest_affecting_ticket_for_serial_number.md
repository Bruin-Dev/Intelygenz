## Get the oldest Service Affecting ticket and its details for an edge

* For each ticket:

    [BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

    * If response status for get ticket details is not ok:
      ```python
      logger.error(
          f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
          f"The oldest Service Affecting ticket cannot be determined."
      )
      ```
      END

    * If ticket has no Service Affecting trouble notes appended in previous monitoring jobs:
      ```python
      logger.info(
          f"Ticket {ticket_id} linked to edge {serial_number} is not being actively used to report "
          f"Service Affecting troubles"
      )
      ```
      _Continue with next ticket_