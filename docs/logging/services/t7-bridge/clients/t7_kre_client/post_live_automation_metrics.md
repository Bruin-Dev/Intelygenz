## Post live automation metrics

Try and make a call to the Konstellations through the SaveLiveMetrics function

* If successful call
  ```python
  logger.info(f'Got response saving live metrics from Konstellation: {response["body"]}')
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error saving live metrics from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f'Got error saving live metrics from Konstellation: {response["body"]}')
  ```
