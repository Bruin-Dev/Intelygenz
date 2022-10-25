import asyncio
import json
import logging
from asyncio import BoundedSemaphore
from datetime import datetime, timedelta

from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone
from shortuuid import uuid

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class StoreLinkMetrics:
    def __init__(self, config, nats_client, mongo_client, scheduler):
        self._config = config
        self._nats_client = nats_client
        self._mongo_client = mongo_client
        self._scheduler = scheduler

        self._semaphore = BoundedSemaphore(10)

    async def start_links_metrics_collector(self):
        logger.info("Scheduling links metrics collector job...")
        tz = timezone(self._config.SCHEDULER_TIMEZONE)
        next_run_time = datetime.now(tz)
        try:
            self._scheduler.add_job(
                self._store_links_metrics,
                "interval",
                minutes=self._config.STORING_INTERVAL_MINUTES,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_links_metrics_collector_job",
            )
        except ConflictingIdError as conflict:
            logger.info(f"Skipping start of links metrics collector job. Reason: {conflict}")

    async def _store_links_metrics(self):
        logger.info(
            f"Getting all edges metrics for velo: {self._config.VELO_HOST} and client"
            f" {self._config.OREILLY_CLIENT_ID}"
        )
        # "data" array of a series has a limit of 1024 items, therefore the max interval is 3 days
        # If the time difference is lesser than 15 min between start and end it will return an empty array response
        start = int(((datetime.utcnow() - timedelta(minutes=15)) - datetime(1970, 1, 1)).total_seconds() * 1000)
        end = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)
        all_edges = await self._get_all_velo_edges(self._config.VELO_HOST, self._config.OREILLY_CLIENT_ID)
        edge_ids_w_link = [edge["id"] for edge in all_edges if edge["links"] != []]
        no_link_edges = [edge["id"] for edge in all_edges if edge["links"] == []]
        logger.info(f"Edges with links: {edge_ids_w_link}")
        logger.info(f"Edges without links (won't be processed): {no_link_edges}")

        process_tasks = [
            self._get_edge_links_series(self._config.VELO_HOST, edge_id, start, end) for edge_id in edge_ids_w_link
        ]
        all_series = await asyncio.gather(*process_tasks, return_exceptions=False)
        curated_series = [series for series in all_series if series != []]
        logger.info(f"Got {len(curated_series)} after removing series with empty responses, inserting in mongo")
        for series in curated_series:
            insert_data = {"velo": self._config.VELO_HOST, "series": series, "start_date": start, "end_date": end}
            self._mongo_client.insert(insert_data)
        logger.info(f"All series data inserted in mongo successfully!")

    async def _get_all_velo_edges(self, host, enterprise_id):
        err_msg = None
        request = {
            "request_id": uuid(),
            "body": {"host": host, "enterprise_id": enterprise_id},
        }
        try:
            logger.info(f"Getting all edges for {host} and enterprise: {enterprise_id}")
            response = await self._nats_client.request("request.enterprises.edges", to_json_bytes(request), timeout=20)
            response = json.loads(response.data)
            logger.info(f"Got all edges Velocloud host {host} and enterprise {enterprise_id}!")
        except Exception as e:
            err_msg = f"An error occurred when getting all edges from Velocloud -> {e}"
            response = None
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300):
                err_msg = (
                    f"Error while retrieving all edges in {self._config.CURRENT_ENVIRONMENT.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )

        if err_msg:
            logger.error(err_msg)
        return response["body"]

    async def _get_edge_links_series(self, host, edge_id, start, end):
        async with self._semaphore:
            err_msg = None
            payload = {
                "enterpriseId": 22,
                "edgeId": edge_id,
                "interval": {"start": start, "end": end},
                "metrics": self._config.METRICS_LIST,
            }
            request = {
                "request_id": uuid(),
                "body": {
                    "host": host,
                    "payload": payload,
                },
            }
            try:
                logger.info(f"Getting links series for {payload}")
                response = await self._nats_client.request(
                    "request.edge.links.series", to_json_bytes(request), timeout=60
                )
                response = json.loads(response.data)
                logger.info(f"Got link series for {payload}!")
            except Exception as e:
                err_msg = f"An error occurred getting link metrics from Velocloud for {payload} -> {e}"
                response = None
            else:
                response_body = response["body"]
                response_status = response["status"]

                if response_status not in range(200, 300):
                    err_msg = (
                        f"Error while retrieving link series for {payload} in "
                        f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                        f"Error {response_status} - {response_body}"
                    )

            if err_msg:
                logger.error(err_msg)
            return response["body"]
