<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# CREATE NEW METRIC

This process describes step by step how to create a new metric, how to test it locally and how to verify that it's
working in production.
Feel free to skip step 1 if the metrics repository already exists in the service you want to add the new metric for.

## 1. Adding metrics repository to the service

First thing you need to do is adding the metric repository to your service if it is not already there, 
for doing that you will need to follow the steps below:

- Add the repository in the `app.py` file
```
from application.repositories.metrics_repository import MetricsRepository


class Container:
    def __init__(self):
        [...]
        # METRICS
        self._metrics_repository = MetricsRepository()
        
        # ACTIONS
        self._my_service = MyService(
            self._event_bus,
            self._logger,
            self._scheduler,
            config,
            self._utils_repository,
            self._metrics_repository
        )
```

For more info please refer to `CREATE_NEW_MICROSERVICE.md`

Once you have the metric repository in the service just create a new python file called `metrics_repository.py`

## 2. Adding a new metric

Existing metrics repositories can be used as references for each metric type use case. Prometheus offers a great
variety of metric types we can add to the project:

### Counter

The counter metric type is used for any value that increases, such as a request count or error count.
Importantly, a counter should never be used for a value that can decrease (for that see Gauges, below).

```python
from prometheus_client import Counter
COMMON_LABELS = ["feature", "system", "topic", "severity", "event"]
CREATE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter("tasks_created", "Tasks created", COMMON_LABELS + CREATE_LABELS)
    
    def __init__(self):
        self._STATIC_LABELS = {
            "feature": "Service name",
            "system": "System name",
            "topic": "Topic name",
            "severity": "<Integer>",
        }
        
    def increment_tasks_created(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()
```

CREATE_LABELS list can be used to expand the metric labels you are going to use. Remember adding any no static label
when calling the `increment_tasks_created_method`.

The counter property `tasks_created` should create 1 new counter: tasks_created_total. By default, it is set to 0.

We can use `rate(task_created[5m])` to calculate the per second rate of creations averaged over the last 5 minutes.

### Gauge

The gauge metric type can be used for values that go down as well as up, such as current memory usage or
the number of items in a queue.

```python
from prometheus_client import Gauge
COMMON_LABELS = ["feature", "system", "topic"]
MEMORY_USAGE_LABELS = []


class MetricsRepository:
    _memory_usage = Gauge("memory_usage", "Memory Usage", COMMON_LABELS + MEMORY_USAGE_LABELS)
    
    [...]
    
    def increment_memory_usage(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._memory_usage.labels(**labels).inc()
    
    def decrement_memory_usage(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._memory_usage.labels(**labels).dec()

    def reset_memory_usage(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._memory_usage.labels(**labels).set(0)
```

The gauge property `memory_usage` should create 1 new counter: memory_usage_inprogress.

We can use the query `avg_over_time(memory_usage[5m])` to calculate the average memory usage over the last 5 minutes.

### Histogram

The histogram metric type measures the frequency of value observations that fall into specific predefined buckets.

```python
from prometheus_client import Histogram

class MetricsRepository:
    _response_latency = Histogram(
        "response_latency",
        "Response latency",
        buckets=[0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20]
    )
    
    def response_latency(self):
        self._response_latency.time()
        # action()

    def observe_latency(self, time_amount):
        self._response_latency.observe(time_amount)
```

The histogram property `response_latency` should create 3 new counters:
response_latency_count, response_latency_sum, and response_latency_bucket.

Time method times a block of code or function, and observe the duration in seconds. Can be used as a function decorator
or context manager.

We can use the following query to calculate the average response latency duration within the last 5 minutes:
`rate(response_latency_sum[5m]) / rate(response_latency_count[5m])`

### Summary

Summaries and histograms share a lot of similarities. So, simply a Histogram is a Summary with quantiles and
percentiles calculation feature added. Summaries preceded histograms, and the recommendation is 
very much to use histograms where possible.

## 3. Testing the new metric

Add your service to the file `metrics-dashboard/prometheus/config/prometheus-local.yml` in order for Prometheus
to start scraping metrics from it.

```yml
-  job_name: 'my-service'

   scrape_interval: 5s
   static_configs:
     - targets: ['my-service:9090']
```

After that you are ready to go, just run your service and prometheus with `docker-compose up my-service prometheus`.

If you go to [localhost:9090/targets](http://localhost:9090/targets) you should be able to see all the services,
and the status of yours should be `UP`.

You can then go to [localhost:9090/graph](http://localhost:9090/graph) in order to monitor the metric you added and
verify that it works as expected.


## 4. Verifying in production

Once you release your MR with the new metric you can start monitoring it in production. Depending on how often the
action we're measuring with the metric you added happens, it might take a while before it shows up.

You can monitor through the Prometheus interface at [prometheus.mettel-automation.net](https://prometheus.mettel-automation.net),
or directly on Grafana through the explorer interface at [grafana.mettel-automation.net/explore](http://grafana.mettel-automation.net/explore)
for a better UX. You'll need to be connected to the VPN in order to access either.

## 5. Querying your metric

In order to query your metric you'll need to use PromQL. For each metric we add, Prometheus creates 2 under the hood:
one for the date it was created and one for the actual value of the metric. They have the suffixes `_created` and `_total`.

The most basic way to monitor your metric would be to query for `my_metric_total`, which will show the current value of that metric.

Since most of the metrics we have are used across many services, you may want to filter yours with labels.
For instance, `my_metric_total{feature="My Service"}` would filter the results to just those collected by your service.

For more information about PromQL please refer to [prometheus.io/docs/prometheus/latest/querying/basics](https://prometheus.io/docs/prometheus/latest/querying/basics)
