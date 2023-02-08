## Add bandwidth to links metrics

* Adding bandwidth data:
```python
logger.info(f"[bandwidth-reports] Adding bandwidth data to link metrics")
```
* For each link metric:
```python
logger.info(f"[bandwidth-report] Adding bandwidth data for edge {link_metric['serial_number']} and interface {link_metric['link']['interface']}")
```