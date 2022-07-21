# VeloCloud fetcher errors when pushing to kafka #

**Metric name:** velocloud_fetcher_to_kafka_messages_status

**Metric type:** Counter

**Data store:** Prometheus

## VeloCloud - Status of Messages sent to Kafka ##

**Description:** Number of OK calls or Errors when pushing data to the kafka server.

**Labels:**

- **schema_name:** <schema_name\>
- **status:** [OK | ERROR]
- **environment:** [develop | master]
