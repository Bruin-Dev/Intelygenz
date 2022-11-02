## Get email inference

Try and make a call to the Konstellations through the GetPrediction function

* If successful call
  ```python
  logger.info(f"Got response getting prediction from Konstellation: {dic_prediction_response}")
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error getting prediction from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f"Got error getting prediction from Konstellation: {e.args[0]}")
  ```