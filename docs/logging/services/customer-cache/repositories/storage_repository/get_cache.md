## Get customer cache for VeloCloud host (VCO)

* If cache exists:
  ```python
  logger.info(f"Cache found for {key}")
  ```
* Otherwise:
  ```python
  logger.warning(f"No cache found for {key}")
  ```