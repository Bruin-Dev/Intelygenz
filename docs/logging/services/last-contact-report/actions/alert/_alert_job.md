## Run Last Contact Report job

```python
logger.info("Requesting all edges with details for alert report")
```

[VelocloudRepository::get_edges](../../repositories/velocloud_repository/get_edges.md)

* If an error took place while fetching edges across all VCOs:
  ```python
  logger.warning("Couldn't retrieve any edge from any of the VCOs. Report won't be sent.")
  ```
  END

* For every edge:
    * If edge was last contacted less than 30 days ago:
      ```python
      logger.info(f"Time elapsed is less than 30 days for {serial_number}")
      ```
      _Continue with next edge_

Compose e-mail with edges last contacted more than or exactly 30 days ago

Deliver e-mail

```python
logger.info("Last Contact Report sent")
```