## Report incident

```python
log.info(f"Reporting incident with payload: {payload}")
log.info(f"to URL {self._base_url}/api/g_mtcm/intelygenz")
```

Call [_request](_request.md), which ultimately makes a call to `POST /api/g_mtcm/intelygenz` with the desired payload.
