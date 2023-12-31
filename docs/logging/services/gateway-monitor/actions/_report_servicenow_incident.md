## Report ServiceNow incident

[ServiceNowRepository::report_incident](../repositories/servicenow_repository/report_incident.md)

* If the result state is "inserted":
    ```python
    logger.info(
        f"A new incident with ID {result['number']} was created in ServiceNow "
        f"for host {gateway['host']} and gateway {gateway['name']}"
    )
    ```
* If the result state is "ignored":
    ```python
    logger.info(
        f"An open incident with ID {result['number']} already existed in ServiceNow "
        f"for host {gateway['host']} and gateway {gateway['name']}"
    )
    ```
* If the result state is "reopened":
    ```python
    logger.info(
        f"A resolved incident with ID {result['number']} was reopened in ServiceNow "
        f"for host {gateway['host']} and gateway {gateway['name']}"
    )
    ```
