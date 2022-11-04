## Get edges across VCOs

```python
logger.info("Getting list of all velo edges")
```

[get_edges](get_edges.md)

```python
logger.info(f"Got all edges from all velos. Took {(time.time() - start_time) // 60} minutes")
```

```python
logger.info("Getting list of logical IDs by each velo edge")
```

[_get_logical_id_by_edge_list](_get_logical_id_by_edge_list.md)

```python
logger.info(f"Got all logical IDs by each velo edge. Took {(time.time() - start_time) // 60} minutes")
```

```python
logger.info(f"Mapping edges to serials...")
```

[_get_all_serials](_get_all_serials.md)

```python
logger.info(f"Amount of edges: {len(edges_with_serial)}")
```

```python
logger.info("Adding links configuration to edges...")
```

[add_edge_config](add_edge_config.md)

```python
logger.info(
    "Finished adding links configuration to edges. Took {(time.time() - start_time) // 60} minutes"
)
```

```python
logger.info(f"Finished building velos + serials map. Took {(time.time() - start_time) // 60} minutes")
```