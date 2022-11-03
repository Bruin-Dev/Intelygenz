# Check if token is created and valid

* If there isn't token
```python
logger.info(f"The token is not created yet")
```

* If the token is expired
```python
logger.info(f"The token is not valid because it is expired")
```