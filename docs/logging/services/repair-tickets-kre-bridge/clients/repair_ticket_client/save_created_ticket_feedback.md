## Save created ticket feedback

Try and make a call to the Konstellations through the SaveCreatedTicketsFeedback function

* If successful call
  ```python
  logger.info(f'Got response saving created ticket feedback from Konstellation: {response["body"]}')
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error saving created ticket feedback from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f'Got error saving created tickets feedback from Konstellation: {response["body"]}')
  ```