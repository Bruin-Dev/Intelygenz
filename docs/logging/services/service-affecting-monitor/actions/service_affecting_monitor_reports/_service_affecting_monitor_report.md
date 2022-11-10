## Generate and send Reoccurring Trouble Report

```python
logger.info(f"Generating all reports for {len(affecting_tickets_per_client)} Bruin clients...")
```

* For each client ID and the Service Affecting tickets related to that customer:

    ```python
    logger.info(f"Processing {len(affecting_tickets)} tickets for client {client_id}...")
    ```

    ```python
    logger.info(f"Getting ticket tasks from {len(affecting_tickets)} tickets for client {client_id}...")
    ```

    ```python
    logger.info(f"Got ticket tasks for client {client_id}")
    ```

    ```python
    logger.info(
        f"Mapping interfaces to counters with the number of tickets where a trouble has been reported for "
        f"client {client_id}..."
    )
    ```

    ```python
    logger.info(
        f"Mapped interfaces to counters. Got {len(report_list)} rows for the report for client {client_id}."
    )
    ```

    ```python
    logger.info(
        f"Filtering out rows with interfaces whose troubles haven't been reported to at least {threshold} "
        f"different tickets for client {client_id}..."
    )
    ```

    ```python
    logger.info(
        f"Rows with interfaces whose troubles haven't been reported to at least {threshold} different tickets "
        f"were filtered out. Got {len(final_report_list)} rows for the report for client {client_id}."
    )
    ```

    ```python
    logger.info(f"Sending report of {len(final_report_list)} rows to client {client_id} via email...")
    ```
  
    ```python
    logger.info(f"Report for client {client_id} sent via email")
    ```