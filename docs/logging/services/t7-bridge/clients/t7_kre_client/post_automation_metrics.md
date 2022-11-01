## Post automation metrics

Try and make a call to the Konstellations through the SaveMetrics function

* If successful call
  ```python
  logger.info(f'Got response saving metrics from Konstellation: {response["body"]}')
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error saving metrics from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f'Got error saving metrics from Konstellation: {response["body"]}')
  ```
