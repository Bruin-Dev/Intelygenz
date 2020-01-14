import json
import yaml
import os
import re

from datetime import datetime

import asyncio
from shortuuid import uuid

from config import config
from igz.packages.Logger.logger_client import LoggerClient
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.nats.clients import NATSClient
from igz.packages.server.api import QuartServer


logger = LoggerClient(config).get_logger()


class Container:

    def __init__(self):
        self.client1 = NATSClient(config, logger=logger)
        self.event_bus = EventBus(logger=logger)
        self.event_bus.set_producer(self.client1)
        self.enterprise_names = []

    def get_new_templating(self, templating, company):
        new_var = {
            "current": {
                "text": company,
                "value": company
            },
            "hide": 2,
            "label": "",
            "name": "enterprise",
            "options": [{
                "selected": True,
                "text": company,
                "value": company
            }],
            "query": company,
            "skipUrlSync": False,
            "type": "constant"
        }

        templating["list"].append(new_var)
        return templating

    def get_company_name(self, company):
        return company.split('|')[0]

    def get_new_dashboard(self, dummy, company, id):
        return {
            "annotations": dummy["annotations"],
            "editable": dummy["editable"],
            "gnetId": dummy["gnetId"],
            "graphTooltip": dummy["graphTooltip"],
            "id": id,
            "iteration": dummy["iteration"],
            "links": dummy["links"],
            "panels": dummy["panels"],
            "refresh": dummy["refresh"],
            "schemaVersion": dummy["schemaVersion"],
            "style": dummy["style"],
            "tags": dummy["tags"],
            "templating": self.get_new_templating(dummy["templating"], company),
            "time": dummy["time"],
            "timepicker": dummy["timepicker"],
            "timezone": dummy["timezone"],
            "title": f'{self.get_company_name(company)} Dashboard',
            "version": dummy["version"]
        }

    def generate_dashboards(self):

        main_path = os.path.dirname(os.path.realpath(__file__))
        dashboards_path = os.path.join(main_path, 'dashboards-definitions')
        dashboard_destination_path = os.path.join(os.sep, 'var', 'lib', 'grafana', 'dashboards')

        with open(os.path.join(dashboards_path, 'dummy', 'dummy.json'), 'r') as f:
            dashboard = json.load(f)

        id = dashboard["id"] + 1
        for c in self.enterprise_names:
            company_name = self.get_company_name(c).replace(' ', '-').lower()

            logger.info(f'Creating dashboard for company {company_name}')
            d = self.get_new_dashboard(dashboard, c, id)

            folder_path = os.path.join(dashboard_destination_path, company_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            logger.info(f'Saving dashboard to folder {folder_path}')
            file_name = os.path.join(
                dashboard_destination_path,
                company_name,
                f'{company_name}-dashboard.json'
            )
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=2)

            logger.info(f'Adding provider to .yaml file')
            yaml_path = os.path.join(os.sep, 'etc', 'grafana', 'provisioning', 'dashboards', 'all.yml')
            new_provider = {
                "name": f'{company_name}-dashboard',
                "org_id": 1,
                "folder": company_name,
                "type": 'file',
                "options": {"path": f'/var/lib/grafana/dashboards/{company_name}'}
            }

            with open(yaml_path, 'r') as f:
                y = yaml.safe_load(f)
                if f'{company_name}-dashboard' not in [p["name"] for p in y["providers"]]:
                    y["providers"].append(new_provider)
            with open(yaml_path, 'w') as f:
                yaml.dump(y, f)

            id += 1

    async def _make_rpc_request(self):
        rpc_request_msg = {
            "request_id": uuid(),
            "filter": ['Titan America|85940|']
        }
        logger.info('Requesting...')
        response = await self.event_bus.rpc_request(
            "request.enterprises.names",
            rpc_request_msg,
            timeout=20
        )
        self.enterprise_names = response["enterprise_names"]
        logger.info(f'Got RPC response with {len(self.enterprise_names)} enterprises')
        print(self.enterprise_names)
        self.generate_dashboards()

    async def start(self):
        logger.info('Starting...')
        await self.event_bus.connect()
        logger.info('Making request...')
        await self._make_rpc_request()

    async def run(self):
        logger.info('Running')
        await self.start()


if __name__ == '__main__':
    logger.info("Grafana dashboard creation started...")
    container = Container()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(container.run())
    logger.info(f'Finished.')
