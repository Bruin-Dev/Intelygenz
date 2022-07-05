# Task Velocloud fetcher errors when to kafka #

**Metric name:** velocloud_fetcher_to_kafka_messages_status

**Type of metric:** Counter

**Data store:** Prometheus

## VeloCloud  - Status of Messages sent to Kafka ##

**Description:** This metrics counts the number of OK calls or Errors when push data to the kafka server.

**Labels:**
- schema_name: Name of the schema
- status: [OK, ERROR]
- environment: [develop, master]