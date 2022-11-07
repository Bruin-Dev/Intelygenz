## Send

```python
log.debug(f"send(rpc_request={rpc_request})")
```

response = nats_client.request

* if response.is_ok()
    ```python
    log.debug(f"_nats_client.rpc_request(subject={self._topic}, payload={payload}) [OK]")
    ```

```python
log.debug(f"send() [OK]")
```