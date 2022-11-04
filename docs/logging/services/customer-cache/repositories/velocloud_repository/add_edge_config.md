## Add links' configuration to edge

```python
logger.info(f"Adding links' configuration to edge {edge}...")
```

[get_links_configuration](get_links_configuration.md)

* If response status for get links' configuration for the edge is not ok:
  ```python
  logger.error(f"Error while getting links configuration for edge {edge_request}")
  ```
  END

```python
logger.info(f"Links' configuration added to edge {edge}")
```