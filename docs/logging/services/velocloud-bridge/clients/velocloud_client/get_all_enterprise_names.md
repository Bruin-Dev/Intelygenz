## Get all enterprise names

* For each available VeloCloud host:

    [get_monitoring_aggregates](get_monitoring_aggregates.md)

    * If response status of get monitoring aggregates for current VeloCloud host is not ok:
      ```python
      logger.error(
          f"Function [get_all_enterprise_names] Error: \n"
          f"Status : {res['status']}, \n"
          f"Error Message: {res['body']}"
      )
      ```

      _Continue to next VeloCloud host_