## Get prediction

Try and make a call to the Konstellations through the Prediction function

* If successful call
  ```python
  logger.info(f"Got response getting predictions from Konstellation: {dic_prediction_response}")
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error getting predictions from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f"Got error getting predictions from Konstellation: {e.args[0]}")
  ```
