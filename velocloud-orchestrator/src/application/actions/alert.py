from igz.packages.eventbus.eventbus import EventBus
from shortuuid import uuid
from datetime import datetime
import json


class Alert:

    def __init__(self, event_bus: EventBus, scheduler, logger):
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._logger = logger

    async def start_alert_job(self):
        # TODO schedule this to be every monday instead
        self._scheduler.add_job(self._alert_process, 'interval', seconds=60, next_run_time=datetime.now(),
                                replace_existing=True, id='_alert_process')

    async def _alert_process(self):
        await self._request_all_edges()

    async def _request_all_edges(self):
        request = dict(request_id=uuid(), filter=[])
        await self._event_bus.publish_message("alert.request.all.edges", json.dumps(request))

    async def _receive_all_edges(self, msg):
        all_edges = json.loads(msg)["edges"]
        edges_to_report = []
        for edge_info in all_edges:
            raw_last_contact = edge_info["edge"]["lastContact"]
            # TODO Improve this
            if '0000-00-00 00:00:00' not in raw_last_contact:
                last_contact = datetime.strptime(raw_last_contact, "%Y-%m-%dT%H:%M:%S.%fZ")
                time_elapsed = datetime.now() - last_contact
                if time_elapsed.days >= 30:
                    edge_for_alert = dict(serial_number=edge_info["edge"]["serialNumber"],
                                          enterprise=edge_info["enterprise"],
                                          last_contact=edge_info["edge"]["lastContact"])
                    edges_to_report.append(edge_for_alert)

        email_obj = dict(request_id=uuid(),
                         email_data=dict(subject="Edge Alert Test", message=json.dumps(edges_to_report, indent=4)))
        await self._event_bus.publish_message("notification.email.request", json.dumps(email_obj))
