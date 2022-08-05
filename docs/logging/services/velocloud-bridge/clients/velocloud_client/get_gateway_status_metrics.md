## Get gateway status metrics

* If there's no client authenticated against the VeloCloud host:
    ```python
    logger.error(f"Cannot find a client to connect to {velocloud_host}")
    ```

    [_start_relogin_job](_start_relogin_job.md)

    [__log_result](__log_result.md)

    END

```python
logger.info(
    f"Getting gateway status metrics for gateway {gateway_id} and host {velocloud_host} in "
    f"interval {interval}..."
)
```
  
Call VeloCloud API endpoint `POST /metrics/getGatewayStatusMetrics` with the set of desired parameters.

* If there's an error while connecting to VeloCloud API:

    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is between `500` and `512` (both inclusive):

    [__log_result](__log_result.md)

    END

* If the status of the HTTP response is `400`:

    [__log_result](__log_result.md)

    END

[__schedule_relogin_job_if_needed](__schedule_relogin_job_if_needed.md)

```python
logger.info(
    f"Got HTTP {response.status} from Velocloud after getting gateway status metrics for gateway {gateway_id} "
    f"and host {velocloud_host} in interval {interval}"
)
```

[__log_result](__log_result.md)