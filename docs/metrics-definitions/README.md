## Metrics Definitons ##

This folder will contain all the metrics created to track functional and business values that improve the overall observability of the system

There will be one markdown file in this folder per metric, the filename will be the metric name and it will contain all their descriptions and all their possible variations.

Naming conventions must follow the Prometheus Best Practices for naming and units: https://prometheus.io/docs/practices/naming/

## List of metrics ##

| Metric Name | Description | File |
| --- | --- | --- |
| tasks_created | Task Creations | [tasks_created.md](./tasks_created.md) |
| tasks_reopened | Task Re-opens | [tasks_reopened.md](./tasks_reopened.md) |
| tasks_forwarded | Task Forwards | [tasks_forwarded.md](./tasks_forwarded.md) |
| tasks_autoresolved | Task Auto-resolves | [tasks_autoresolved.md](./tasks_autoresolved.md) |
| velocloud_fetcher_to_kafka_messages_attempts | Velocloud fetcher attempts to kafka | [velocloud_fetcher_to_kafka_messages_attempts.md](./velocloud_fetcher_to_kafka_messages_attempts.md) |
| velocloud_fetcher_to_kafka_messages_status | Velocloud fetcher errors when to kafka | [velocloud_fetcher_to_kafka_messages_status.md](./velocloud_fetcher_to_kafka_messages_status.md) |
