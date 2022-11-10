## Map edges from cache of customers with links metrics and Bruin contact information

* For each set of link metrics:

    * If link's edge is not in the cache of customers:
      ```python
      logger.warning(f"No cached info was found for edge {serial_number}. Skipping...")
      ```
      _Continue with next set of link metrics_
  
    * If tickets opened for this link should use a fixed contact information:
      ```python
      logger.info(f"Using default contact info for edge {serial_number} and client {client_id}")
      ```
    * Otherwise:
      ```python
      logger.info(f"Using site-specific contact info for edge {serial_number} and client {client_id}")
      ```