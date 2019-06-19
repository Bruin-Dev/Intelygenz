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
        # self._scheduler.add_job(self._alert_process, 'interval', seconds=60, next_run_time=datetime.now(),
        #                         replace_existing=True, id='_alert_process')
        await self._alert_process()

    async def _alert_process(self):
        await self._request_all_edges()

    async def _request_all_edges(self):
        request = dict(request_id=uuid(), filter=[])
        await self._event_bus.publish_message("alert.request.all.edges", json.dumps(request))

    async def _receive_all_edges(self, msg):
        all_edges = json.loads(msg)["edges"]
        email_obj = dict(request_id=uuid(),
                         email_data=dict(subject="Edge Alert Test", message=json.dumps(all_edges, indent=4)))
        await self._event_bus.publish_message("notification.email.request", json.dumps(email_obj))
