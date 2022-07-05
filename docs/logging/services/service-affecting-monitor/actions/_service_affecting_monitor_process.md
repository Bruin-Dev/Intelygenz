## Service Affecting process Documentation

```
self._logger.info(f"Starting Service Affecting Monitor process now...")
```

* [Get cache for affecting monitoring](../repositories/customer_cache_repository/get_cache_for_affecting_monitoring.md)
* Check if customer cache is empty
    ```
    self._logger.info("Got an empty customer cache. Process cannot keep going.")
    ```
* [Latency Check](_latency_check.md)
* [Packet Loss Check](_packet_loss_check.md)
* [Jitter Check](_jitter_check.md)
* [Bandwidth Check](_bandwidth_check.md)
* [Bouncing Check](_bouncing_check.md)
* [Run Autoresolve process](_run_autoresolve_process.md)

```
self._logger.info(f"Finished processing all links! Took {round((time.time() - start_time) / 60, 2)} minutes")
```