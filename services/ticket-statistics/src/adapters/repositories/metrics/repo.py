from prometheus_client import Gauge


class MetricsRepository:
    metrics = {}

    def __init__(self):
        for key in self.create_statistics_object():
            self.metrics[key] = Gauge(f'stat_{key}', '')

    @staticmethod
    def create_statistics_object(
            tasks_created=0, tasks_reopened=0, no_touch_resolution=0, ai_resolved_tasks=0, auto_resolved_tasks=0,
            devices_rebooted=0, devices_monitoring=0, hnoc_work_queue_reduced=0, ai_forwarded_tasks=0,
            dispatch_reminders=0, dispatch_monitored=0, average_time_to_resolve=0, average_time_to_document=0,
            average_time_to_acknowledge=0, ipa_headcount_equivalent=0, quarantine_time=3):
        return {
            'ai_forwarded_tasks': ai_forwarded_tasks,
            'tasks_created': tasks_created,
            'tasks_reopened': tasks_reopened,
            'no_touch_resolution': no_touch_resolution,
            'ai_resolved_tasks': ai_resolved_tasks,
            'auto_resolved_tasks': auto_resolved_tasks,
            'devices_rebooted': devices_rebooted,
            'devices_monitoring': devices_monitoring,
            'hnoc_work_queue_reduced': hnoc_work_queue_reduced,
            'dispatch_reminders': dispatch_reminders,
            'dispatch_monitored': dispatch_monitored,
            'average_time_to_resolve': average_time_to_resolve,
            'average_time_to_document': average_time_to_document,
            'average_time_to_acknowledge': average_time_to_acknowledge,
            'ipa_headcount_equivalent': ipa_headcount_equivalent,
            'quarantine_time': quarantine_time,
        }

    def set_statistics(self, statistics):
        for key, value in statistics.items():
            self.metrics[key].set(value)
