## Metrics Definitions ##

This folder will contain all the metrics created to track functional and business values that improve the overall observability of the system.

There will be one markdown file per metric in this folder. The filename will be the metric name and it will contain all the descriptions and possible label combinations.

Naming conventions must follow the [Prometheus Best Practices for naming and units](https://prometheus.io/docs/practices/naming/).

## List of metrics ##

| Metric | Description |
| ------ | ----------- |
| [tasks_created](./tasks_created.md) | Task Creations |
| [tasks_reopened](./tasks_reopened.md) | Task Re-Opens |
| [tasks_forwarded](./tasks_forwarded.md) | Task Forwards |
| [tasks_autoresolved](./tasks_autoresolved.md) | Task Auto-Resolves |
| [velocloud_fetcher_to_kafka_messages_attempts](./velocloud_fetcher_to_kafka_messages_attempts.md) | VeloCloud fetcher attempts to kafka |
| [velocloud_fetcher_to_kafka_messages_status](./velocloud_fetcher_to_kafka_messages_status.md) | VeloCloud fetcher errors when pushing to kafka |
