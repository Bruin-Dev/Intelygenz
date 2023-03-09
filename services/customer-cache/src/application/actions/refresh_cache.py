import asyncio
import base64
import csv
import json
import logging
from copy import deepcopy
from datetime import datetime
from typing import List, NoReturn

from application.repositories import EdgeIdentifier
from apscheduler.jobstores.base import ConflictingIdError
from pytz import timezone
from pyzipcode import ZipCodeDatabase
from shortuuid import uuid
from tenacity import retry, stop_after_delay, wait_exponential, wait_random

logger = logging.getLogger(__name__)


class RefreshCache:
    def __init__(
        self,
        config,
        scheduler,
        storage_repository,
        bruin_repository,
        velocloud_repository,
        notifications_repository,
        email_repository,
    ):
        self._config = config
        self._scheduler = scheduler
        self._storage_repository = storage_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._email_repository = email_repository
        self._serials_with_multiple_inventories = {}
        self._zip_db = ZipCodeDatabase()
        self._semaphore = asyncio.BoundedSemaphore(self._config.REFRESH_CONFIG["semaphore"])

        self.__reset_state()

    def __reset_state(self):
        self._invalid_edges = {}

    async def _refresh_cache(self):
        @retry(wait=wait_random(min=120, max=300), reraise=True)
        async def _refresh_cache():
            if not self._need_to_refresh_cache():
                logger.info("Cache refresh is not due yet. Skipping refresh process...")
                return

            self.__reset_state()

            velocloud_hosts = sum([list(filter_.keys()) for filter_ in self._config.REFRESH_CONFIG["velo_servers"]], [])
            for host in velocloud_hosts:
                self._invalid_edges[host] = []

            logger.info("Starting job to refresh the cache of edges...")
            logger.info(f"Velocloud hosts that are going to be cached: {', '.join(velocloud_hosts)}")

            logger.info("Claiming edges for the hosts specified in the config...")
            edge_list = await self._velocloud_repository.get_all_velo_edges()

            if not edge_list:
                refresh_attempts_count = _refresh_cache.retry.statistics["attempt_number"]
                if refresh_attempts_count >= self._config.REFRESH_CONFIG["attempts_threshold"]:
                    error_message = (
                        "Too many consecutive failures happened while trying "
                        "to claim the list of edges from Velocloud"
                    )
                    await self._notifications_repository.send_slack_message(error_message)
                    raise Exception(error_message)

                logger.warning(f"Couldn't find any edge to refresh the cache. Re-trying job...")
                err_msg = "Couldn't find any edge to refresh the cache"
                raise Exception(err_msg)

            logger.info(f"Distinguishing {len(edge_list)} edges per Velocloud host...")
            split_host_dict = {}
            for edge_with_serial in edge_list:
                host_ = edge_with_serial["edge"]["host"]
                split_host_dict.setdefault(host_, [])
                split_host_dict[host_].append(edge_with_serial)

            logger.info("Refreshing cache for each of the hosts...")
            tasks = [self._partial_refresh_cache(host, split_host_dict[host]) for host in split_host_dict]
            await asyncio.gather(*tasks, return_exceptions=True)

            self._storage_repository.update_refresh_date()
            await self._send_email_multiple_inventories()
            logger.info("Finished refreshing cache!")

        try:
            await _refresh_cache()
        except Exception as e:
            logger.error(f"An error occurred while refreshing the cache -> {e}")
            slack_message = f"Maximum retries happened while while refreshing the cache cause of error was {e}"
            await self._notifications_repository.send_slack_message(slack_message)

    async def schedule_cache_refresh(self):
        logger.info(
            f"Scheduled to refresh cache every {self._config.REFRESH_CONFIG['refresh_map_minutes'] // 60} hours"
        )
        logger.info(
            f"Scheduled to check if refresh is needed every "
            f"{self._config.REFRESH_CONFIG['refresh_check_interval_minutes']} minutes"
        )
        try:
            self._scheduler.add_job(
                self._refresh_cache,
                "interval",
                minutes=self._config.REFRESH_CONFIG["refresh_check_interval_minutes"],
                next_run_time=datetime.now(timezone(self._config.TIMEZONE)),
                replace_existing=False,
                id="_refresh_cache",
            )
        except ConflictingIdError:
            logger.warning(
                f"There is a job scheduled for refreshing the cache already. No new job is going to be scheduled."
            )

    async def _partial_refresh_cache(self, host, edge_list):
        logger.info(f"Filtering the list of edges for host {host}")
        tasks = [self._filter_edge_list(edge) for edge in edge_list]
        cache = [edge for edge in await asyncio.gather(*tasks) if edge is not None]
        logger.info(f"Finished filtering edges for host {host}")

        ha_serials = [edge["ha_serial_number"] for edge in cache if edge["ha_serial_number"] is not None]
        logger.info(f"Adding {len(ha_serials)} HA edges as standalone edges to cache of host {host}...")
        self._add_ha_devices_to_cache(cache)
        logger.info(f"Finished adding HA edges to cache of host {host}")

        if len(cache) == 0:
            error_msg = (
                f"Cache for host {host} was empty after cross referencing with Bruin."
                f" Check if Bruin is returning errors when asking for management statuses of the host"
            )
            logger.error(error_msg)
            await self._notifications_repository.send_slack_message(error_msg)
        else:
            stored_cache = self._storage_repository.get_cache(host)

            logger.info(
                f"Crossing currently stored cache ({len(stored_cache)} edges) with new one ({len(cache)} edges)..."
            )
            crossed_cache = self._cross_stored_cache_and_new_cache(stored_cache=stored_cache, new_cache=cache)
            logger.info(f"Crossed cache of host {host} has {len(crossed_cache)} edges")

            logger.info(f"Removing {len(self._invalid_edges[host])} invalid edges from crossed cache of host {host}...")
            final_cache = [
                edge for edge in crossed_cache if EdgeIdentifier(**edge["edge"]) not in self._invalid_edges[host]
            ]
            logger.info(f"Invalid edges removed from cache! Final cache has {len(final_cache)} edges")

            logger.info(f"Storing cache of {len(final_cache)} edges to Redis for host {host}")
            self._storage_repository.set_cache(host, final_cache)
            await self._send_email_snapshot(host=host, old_cache=stored_cache, new_cache=crossed_cache)
            logger.info(f"Finished storing cache for host {host}")

    @staticmethod
    def _add_ha_devices_to_cache(cache: List[dict]):
        new_edges = []

        logger.info(f"Adding HA edges to the cache (current size: {len(cache)} edges)")
        for edge in cache:
            ha_serial = edge.get("ha_serial_number")
            if ha_serial is None:
                logger.info(f"Edge {edge['serial_number']} doesn't have a HA partner. Skipping...")
                continue

            copy = deepcopy(edge)
            copy["serial_number"], copy["ha_serial_number"] = copy["ha_serial_number"], copy["serial_number"]
            new_edges.append(copy)

        cache.extend(new_edges)
        logger.info(f"{len(new_edges)} HA edges added to the cache (current size: {len(cache)} edges)")

    @staticmethod
    def _cross_stored_cache_and_new_cache(stored_cache: List[dict], new_cache: List[dict]) -> List[dict]:
        stored_devices_by_serial = {edge["serial_number"]: edge for edge in stored_cache}
        new_devices_by_serial = {edge["serial_number"]: edge for edge in new_cache}

        # If a device is in both caches, its info in new_cache will overwrite stored_cache's
        # If a device is only in one of the caches, it will be added to the final cache
        crossed_cache = {
            **stored_devices_by_serial,
            **new_devices_by_serial,
        }
        return list(crossed_cache.values())

    async def _filter_edge_list(self, edge_with_serial):
        host = edge_with_serial["edge"]["host"]
        serial_number = edge_with_serial["serial_number"]

        edge_identifier = EdgeIdentifier(**edge_with_serial["edge"])

        @retry(
            wait=wait_exponential(
                multiplier=self._config.REFRESH_CONFIG["multiplier"], min=self._config.REFRESH_CONFIG["min"]
            ),
            stop=stop_after_delay(self._config.REFRESH_CONFIG["stop_delay"]),
            reraise=True,
        )
        async def _filter_edge_list():
            async with self._semaphore:
                logger.info(f"Checking if edge {serial_number} should be monitored...")

                client_info_response = await self._bruin_repository.get_client_info(serial_number)
                client_info_response_status = client_info_response["status"]
                if client_info_response_status not in range(200, 300):
                    logger.error(f"Error while fetching client info for edge {serial_number}: {client_info_response}")
                    return

                client_info_response_body = client_info_response["body"]
                if len(client_info_response_body) > 1:
                    logger.info(f"Edge {serial_number} has {len(client_info_response_body)} inventories in Bruin")
                    self._serials_with_multiple_inventories[serial_number] = client_info_response_body

                if not client_info_response_body:
                    logger.warning(f"Edge with serial {serial_number} doesn't have any Bruin client info associated")
                    self._invalid_edges[host].append(edge_identifier)
                    return

                bruin_client_info = client_info_response_body[0]
                client_id = bruin_client_info.get("client_id")

                inventory_attributes_response = await self._bruin_repository.get_inventory_attributes(
                    client_id, serial_number
                )
                inventory_attributes_response_status = inventory_attributes_response["status"]
                if inventory_attributes_response_status not in range(200, 300):
                    logger.error(
                        f"Error while fetching inventory attributes for edge {serial_number}: "
                        f"{inventory_attributes_response}"
                    )
                    return

                inventory_attributes_response_body = inventory_attributes_response["body"]
                management_status = self._bruin_repository.get_management_status_from_inventory_attributes(
                    inventory_attributes_response_body
                )

                if not self._bruin_repository.is_management_status_active(management_status):
                    logger.warning(f"Management status is not active for {edge_identifier}. Skipping...")
                    self._invalid_edges[host].append(edge_identifier)
                    return
                else:
                    if (
                        management_status == "Pending"
                        and client_id in self._config.REFRESH_CONFIG["blacklisted_client_ids"]
                    ):
                        logger.warning(
                            f"Edge ({serial_number}) has management_status: Pending and has a blacklisted"
                            f"client_id: {client_id}. Skipping..."
                        )
                        self._invalid_edges[host].append(edge_identifier)
                        return
                    logger.info(f"Management status for {serial_number} seems active")

                logical_ids = edge_with_serial["logical_ids"]
                logical_ids_with_access_types = self._add_access_type_to_logical_ids(
                    inventory_attributes_response_body, logical_ids
                )

                site_id = bruin_client_info["site_id"]
                site_details_response = await self._bruin_repository.get_site_details(client_id, site_id)
                if site_details_response["status"] not in range(200, 300):
                    logger.error(f"Error while fetching site details for edge {serial_number}: {site_details_response}")
                    return

                site_details: dict = site_details_response["body"]
                site_details["tzOffset"] = self._get_tz_offset(site_details)

                ticket_contact_response = await self._bruin_repository.get_ticket_contact(client_id)
                if ticket_contact_response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while fetching ticket contact details for edge {serial_number}: "
                        f"{ticket_contact_response}"
                    )
                    return

                ticket_contact_details: dict = next(iter(ticket_contact_response["body"]), None)
                ticket_contact_additional_subscribers = ticket_contact_response["body"][1:]

                return {
                    "edge": edge_with_serial["edge"],
                    "edge_name": edge_with_serial["edge_name"],
                    "last_contact": edge_with_serial["last_contact"],
                    "logical_ids": logical_ids_with_access_types,
                    "serial_number": serial_number,
                    "ha_serial_number": edge_with_serial["ha_serial_number"],
                    "bruin_client_info": bruin_client_info,
                    "site_details": site_details,
                    "ticket_contact_details": ticket_contact_details,
                    "ticket_contact_additional_subscribers": ticket_contact_additional_subscribers,
                    "links_configuration": edge_with_serial["links_configuration"],
                }

        try:
            return await _filter_edge_list()
        except Exception as e:
            logger.error(f"An error occurred while checking if edge {serial_number} should be cached or not -> {e}")

    def _add_access_type_to_logical_ids(self, inventory_attributes_response_body, logical_ids):
        logical_ids_with_access_types = []
        for logical_id in logical_ids:
            attr_key = f'{logical_id["interface_name"]} Access Type'
            access_type = [
                attribute["value"]
                for attribute in inventory_attributes_response_body["attributes"]
                if attribute["key"] == attr_key
            ]
            if len(access_type) > 0:
                access_type = access_type[0]
            else:
                access_type = None

            logical_id_with_access_type = logical_id
            logical_id_with_access_type["access_type"] = access_type
            logical_ids_with_access_types.append(logical_id_with_access_type)

        return logical_ids_with_access_types

    async def _send_email_snapshot(self, host, old_cache, new_cache):
        logger.info("Sending email with snapshots of cache...")
        email_obj = self._format_email_object(host, old_cache, new_cache)
        response = await self._email_repository.send_email(email_obj)
        logger.info(f"Response from sending email: {json.dumps(response)}")

    async def _send_email_multiple_inventories(self):
        if self._serials_with_multiple_inventories:
            message = f"Alert. Detected some edges with more than one status. {self._serials_with_multiple_inventories}"
            await self._notifications_repository.send_slack_message(message)
            logger.warning(message)
            email_obj = self._format_alert_email_object()
            logger.info(
                f"Sending mail with serials having multiples inventories to  "
                f"{email_obj['body']['email_data']['recipient']}"
            )
            response = await self._email_repository.send_email(email_obj)
            logger.info(f"Response from sending email with serials having multiple inventories: {json.dumps(response)}")
        else:
            logger.info("No edges with multiple Bruin inventories were detected")

    def _format_email_object(self, host, old_cache, new_cache):
        now = datetime.utcnow().strftime("%B %d %Y - %H:%M:%S")
        old_cache_csv = self._generate_csv_bytes_from_cache(f"old_cache_{host}.csv", old_cache)
        new_cache_csv = self._generate_csv_bytes_from_cache(f"new_cache_{host}.csv", new_cache)
        return {
            "request_id": uuid(),
            "body": {
                "email_data": {
                    "subject": f"Customer cache snapshots. Environment: {self._config.ENVIRONMENT_NAME}. Host: {host}. "
                    f"{now}",
                    "recipient": self._config.REFRESH_CONFIG["email_recipient"],
                    "text": "this is the accessible text for the email",
                    "html": f"In this email you will see attached 2 CSV files: the prior and current status of the "
                    f"customer cache for the host {host}."
                    f"Please note that timestamps in the files and in the subject are in UTC.",
                    "images": [],
                    "attachments": [
                        {"name": f"old_customer_cache_{host}_{now}.csv", "data": old_cache_csv},
                        {"name": f"new_customer_cache_{host}_{now}.csv", "data": new_cache_csv},
                    ],
                },
            },
        }

    def _format_alert_email_object(self):
        now = datetime.utcnow().strftime("%B %d %Y - %H:%M:%S")
        text = ""
        for serial in self._serials_with_multiple_inventories.keys():
            text += f"<p>Serial: {serial} and items: {self._serials_with_multiple_inventories[serial]}<p></br>"
        return {
            "request_id": uuid(),
            "body": {
                "email_data": {
                    "subject": f"Serials with multiple inventory items ({now})",
                    "recipient": self._config.REFRESH_CONFIG["email_recipient"],
                    "text": "this is the accessible text for the email",
                    "html": f"<p>In this email you will see the serials with more than one inventory items</p></br>"
                    f"{text}",
                    "images": [],
                    "attachments": [],
                }
            },
        }

    @staticmethod
    def _generate_csv_bytes_from_cache(file_name, cache):
        titles = [
            "Serial Number",
            "Bruin Client ID",
            "Bruin Client Name",
            "Velo Host",
            "Velo Enterprise ID",
            "Velo Edge ID",
            "Last Contact",
            "Logical IDs",
        ]
        rows = [
            [
                item["serial_number"],
                item["bruin_client_info"]["client_id"],
                item["bruin_client_info"]["client_name"],
                item["edge"]["host"],
                item["edge"]["enterprise_id"],
                item["edge"]["edge_id"],
                item["last_contact"],
                item["logical_ids"],
            ]
            for item in cache
        ]
        with open(f"./{file_name}", "w", encoding="utf-8") as csvfile:
            filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(titles)
            for row in rows:
                filewriter.writerow(row)
        with open(f"./{file_name}", "r", encoding="utf-8") as csvfile:
            payload = csvfile.read()
            return base64.b64encode(payload.encode("utf-8")).decode("utf-8")

    def _need_to_refresh_cache(self):
        logger.info("Checking if it is time to refresh the cache...")
        next_refresh_date = self._storage_repository.get_refresh_date()

        is_time = True
        if next_refresh_date:
            now = datetime.utcnow()
            is_time = now > next_refresh_date

        logger.info(f"Is time to refresh cache? {is_time}")
        return is_time

    def _get_tz_offset(self, site_details):
        try:
            tz_name = site_details["timeZone"]

            if tz_name:
                tz_offset = self._get_offset_from_tz_name(f"US/{tz_name}")
            else:
                zip_code = site_details["address"]["zip"].split("-")[0]
                tz_offset = self._zip_db.get(zip_code).timezone
        except Exception:
            tz_offset = self._get_offset_from_tz_name(self._config.TIMEZONE)

        return tz_offset

    @staticmethod
    def _get_offset_from_tz_name(tz_name):
        tz = timezone(tz_name)
        tz_offset = datetime.now(tz).strftime("%z")
        return int(tz_offset[0:3])
