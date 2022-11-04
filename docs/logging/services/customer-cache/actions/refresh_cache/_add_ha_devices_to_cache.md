## Extend cache with High Availability (HA) edges

```python
logger.info(f"Adding HA edges to the cache (current size: {len(cache)} edges)")
```

* For each edge:
    * If the edge doesn't have HA configured:
      ```python
      logger.info(f"Edge {edge['serial_number']} doesn't have a HA partner. Skipping...")
      ```
      _Continue with next edge_

```python
logger.info(f"{len(new_edges)} HA edges added to the cache (current size: {len(cache)} edges)")
```