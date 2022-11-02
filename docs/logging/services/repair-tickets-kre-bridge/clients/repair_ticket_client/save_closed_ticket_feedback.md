## Save closed ticket feedback

Try and make a call to the Konstellations through the SaveClosedTicketsFeedback function

* If successful call
  ```python
  logger.info(f'Got response saving closed ticket feedback from Konstellation: {response["body"]}')
  ```
* Catches a grpc.RpcError
  ```python
  logger.error(f'Got grpc error saving closed ticket feedback from Konstellation: {response["body"]}')
  ```

* Catches a general exception
  ```python
  logger.error(f'Got error saving closed tickets feedback from Konstellation: {response["body"]}')
  ```