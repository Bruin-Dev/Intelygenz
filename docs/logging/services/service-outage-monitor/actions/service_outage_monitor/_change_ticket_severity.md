## Change ticket severity

```python
logger.info(f"Attempting to change severity level of ticket {ticket_id}...")
```

* If the edge is under a Hard Down or Soft Down outage:
    ```python
    logger.info(
        f"Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue "
        f"is that edge {serial_number} is offline."
    )
    ```

    [BruinRepository::get_ticket](../../repositories/bruin_repository/get_ticket.md)

    * If response status for get ticket is not ok:
      ```python
      logger.error(
          f"Error while getting overview of ticket {ticket_id}: {get_ticket_response}. "
          f"Skipping ticket severity change..."
      )
      ```
      END

    * If ticket's severity is already set to 2 (Medium/High):
      ```python
      logger.info(
          f"Ticket {ticket_id} is already in severity level {target_severity}, so there is no need "
          "to change it."
      )
      ```
      END

    [BruinRepository::change_ticket_severity_for_offline_edge](../../repositories/bruin_repository/change_ticket_severity_for_offline_edge.md)

    * If response status for change ticket severity is not ok:
      ```python
      logger.error(
          f"Error while changing severity of ticket {ticket_id}: {result}. Skipping ticket severity change..."
      )
      ```
      END

    ```python
    logger.info(f"Finished changing severity level of ticket {ticket_id} to {target_severity}!")
    ```

    END

* If the edge is under a Link Down outage:
    * If Bruin returned a 409, 471, or 472 status while trying to create the ticket:

        [BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

        * If response status for get ticket details is not ok:
          ```python
          logger.error(
              f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
              f"Skipping ticket severity change..."
          )
          ```
          END

        * If the ticket task related to the edge is not the only one currently open:
          ```python
          logger.info(
              f"Severity level of ticket {ticket_id} will remain the same, as the root cause of the outage "
              f"issue is that at least one link of edge {serial_number} is disconnected, and this ticket "
              f"has multiple unresolved tasks."
          )
          ```
          END

        ```python
        logger.info(
            f"Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue "
            f"is that at least one link of edge {serial_number} is disconnected, and this ticket has a single "
            "unresolved task."
        )
        ```

        [BruinRepository::get_ticket](../../repositories/bruin_repository/get_ticket.md)

        * If response status for get ticket is not ok:
          ```python
          logger.error(
              f"Error while getting overview of ticket {ticket_id}: {get_ticket_response}. "
              f"Skipping ticket severity change..."
          )
          ```
          END

        * If ticket's severity is already set to 2 (Medium/High):
          ```python
          logger.info(
              f"Ticket {ticket_id} is already in severity level {target_severity}, so there is no need "
              "to change it."
          )
          ```
          END

        [BruinRepository::change_ticket_severity_for_disconnected_links](../../repositories/bruin_repository/change_ticket_severity_for_disconnected_links.md)

        * If response status for change ticket severity is not ok:
          ```python
          logger.error(
              f"Error while changing severity of ticket {ticket_id}: {result}. Skipping ticket severity change..."
          )
          ```
          END

        ```python
        logger.info(f"Finished changing severity level of ticket {ticket_id} to {target_severity}!")
        ```

        END