## Save outputs

Try and make a call to the Konstellations through the SaveOutputs function

* If successful call
  ```python
  logger.info(f'Got response saving outputs from Konstellation: {response["body"]}')
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error saving outputs from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f'Got error saving outputs from Konstellation: {response["body"]}')
  ```