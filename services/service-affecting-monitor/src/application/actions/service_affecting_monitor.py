import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional

from application import AFFECTING_NOTE_REGEX, LINK_INFO_REGEX, REMINDER_NOTE_REGEX, AffectingTroubles, ForwardQueues
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from framework.storage.task_dispatcher_client import TaskTypes
from pytz import timezone

logger = logging.getLogger(__name__)


class ServiceAffectingMonitor:
    def __init__(
        self,
        scheduler,
        task_dispatcher_client,
        config,
        metrics_repository,
        bruin_repository,
        velocloud_repository,
        customer_cache_repository,
        notifications_repository,
        ticket_repository,
        trouble_repository,
        utils_repository,
    ):
        self._scheduler = scheduler
        self._task_dispatcher_client = task_dispatcher_client
        self._config = config
        self._metrics_repository = metrics_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._customer_cache_repository = customer_cache_repository
        self._notifications_repository = notifications_repository
        self._ticket_repository = ticket_repository
        self._trouble_repository = trouble_repository
        self._utils_repository = utils_repository

        self.__autoresolve_semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG["autoresolve"]["semaphore"])

        self.__reset_state()

    def __reset_state(self):
        self._customer_cache = []

    async def start_service_affecting_monitor(self, exec_on_start=False):
        logger.info("Scheduling Service Affecting Monitor job...")
        next_run_time = undefined

        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            logger.info("Service Affecting Monitor job is going to be executed immediately")

        try:
            self._scheduler.add_job(
                self._service_affecting_monitor_process,
                "interval",
                minutes=self._config.MONITOR_CONFIG["monitoring_minutes_interval"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_service_affecting_monitor_process",
            )
        except ConflictingIdError as conflict:
            logger.error(f"Skipping start of Service Affecting Monitoring job. Reason: {conflict}")

    async def _service_affecting_monitor_process(self):
        self.__reset_state()

        logger.info(f"Starting Service Affecting Monitor process now...")
        start_time = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        if customer_cache_response["status"] not in range(200, 300) or customer_cache_response["status"] == 202:
            logger.error(
                f"Error while getting VeloCloud's customer cache: {customer_cache_response}. "
                f"Skipping Service Affecting monitoring process..."
            )
            return

        self._customer_cache: list = customer_cache_response["body"]
        if not self._customer_cache:
            logger.warning("Got an empty customer cache. Skipping Service Affecting monitoring process...")
            return

        self._default_contact_info_by_client_id = self._get_default_contact_info_by_client_id()
        self._customer_cache = [
            edge
            for edge in customer_cache_response["body"]
            if edge["bruin_client_info"]["client_id"] in self._default_contact_info_by_client_id
        ]

        # for_wireless
        await self._latency_check(for_wireless=False)
        await self._packet_loss_check(for_wireless=False)
        await self._jitter_check(for_wireless=False)
        await self._bandwidth_check(for_wireless=False)
        await self._bouncing_check(for_wireless=False)

        # for_wired
        await self._latency_check(for_wireless=True)
        await self._packet_loss_check(for_wireless=True)
        await self._jitter_check(for_wireless=True)
        await self._bandwidth_check(for_wireless=True)
        await self._bouncing_check(for_wireless=True)

        await self._run_autoresolve_process()

        logger.info(f"Finished processing all links! Took {round((time.time() - start_time) / 60, 2)} minutes")

    def _get_default_contact_info_by_client_id(self):
        contact_info_by_host_and_client_id = self._config.MONITOR_CONFIG["contact_info_by_host_and_client_id"]
        contact_info_by_client_id = {}

        for host in contact_info_by_host_and_client_id:
            if "*" in contact_info_by_host_and_client_id[host]:
                contact_info = contact_info_by_host_and_client_id[host]["*"]
                for edge in self._customer_cache:
                    if edge["edge"]["host"] == host:
                        client_id = edge["bruin_client_info"]["client_id"]
                        contact_info_by_client_id[client_id] = contact_info
            else:
                for client_id, contact_info in contact_info_by_host_and_client_id[host].items():
                    contact_info_by_client_id[client_id] = contact_info

        return contact_info_by_client_id

    def _should_use_default_contact_info(self, client_id: int, edge: dict):
        if client_id in self._config.MONITOR_CONFIG["customers_to_always_use_default_contact_info"]:
            return True

        return False

    def _structure_links_metrics(self, links_metrics: list, events: dict = None) -> list:
        result = []

        for link_info in links_metrics:
            velocloud_host = link_info["link"]["host"]
            enterprise_name = link_info["link"]["enterpriseName"]
            enterprise_id = link_info["link"]["enterpriseId"]
            edge_name = link_info["link"]["edgeName"]
            edge_state = link_info["link"]["edgeState"]

            if edge_state is None:
                logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
                continue

            if edge_state == "NEVER_ACTIVATED":
                logger.info(
                    f"Edge {edge_name} in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has never been activated. Skipping..."
                )
                continue

            structured_link = {
                "edge_status": {
                    "enterpriseName": link_info["link"]["enterpriseName"],
                    "enterpriseId": link_info["link"]["enterpriseId"],
                    "enterpriseProxyId": link_info["link"]["enterpriseProxyId"],
                    "enterpriseProxyName": link_info["link"]["enterpriseProxyName"],
                    "edgeName": link_info["link"]["edgeName"],
                    "edgeState": link_info["link"]["edgeState"],
                    "edgeSystemUpSince": link_info["link"]["edgeSystemUpSince"],
                    "edgeServiceUpSince": link_info["link"]["edgeServiceUpSince"],
                    "edgeLastContact": link_info["link"]["edgeLastContact"],
                    "edgeId": link_info["link"]["edgeId"],
                    "edgeSerialNumber": link_info["link"]["edgeSerialNumber"],
                    "edgeHASerialNumber": link_info["link"]["edgeHASerialNumber"],
                    "edgeModelNumber": link_info["link"]["edgeModelNumber"],
                    "edgeLatitude": link_info["link"]["edgeLatitude"],
                    "edgeLongitude": link_info["link"]["edgeLongitude"],
                    "host": link_info["link"]["host"],
                },
                "link_status": {
                    "interface": link_info["link"]["interface"],
                    "internalId": link_info["link"]["internalId"],
                    "linkState": link_info["link"]["linkState"],
                    "linkLastActive": link_info["link"]["linkLastActive"],
                    "linkVpnState": link_info["link"]["linkVpnState"],
                    "linkId": link_info["link"]["linkId"],
                    "linkIpAddress": link_info["link"]["linkIpAddress"],
                    "displayName": link_info["link"]["displayName"],
                    "isp": link_info["link"]["isp"],
                },
                "link_metrics": {
                    "bytesTx": link_info["bytesTx"],
                    "bytesRx": link_info["bytesRx"],
                    "packetsTx": link_info["packetsTx"],
                    "packetsRx": link_info["packetsRx"],
                    "totalBytes": link_info["totalBytes"],
                    "totalPackets": link_info["totalPackets"],
                    "p1BytesRx": link_info["p1BytesRx"],
                    "p1BytesTx": link_info["p1BytesTx"],
                    "p1PacketsRx": link_info["p1PacketsRx"],
                    "p1PacketsTx": link_info["p1PacketsTx"],
                    "p2BytesRx": link_info["p2BytesRx"],
                    "p2BytesTx": link_info["p2BytesTx"],
                    "p2PacketsRx": link_info["p2PacketsRx"],
                    "p2PacketsTx": link_info["p2PacketsTx"],
                    "p3BytesRx": link_info["p3BytesRx"],
                    "p3BytesTx": link_info["p3BytesTx"],
                    "p3PacketsRx": link_info["p3PacketsRx"],
                    "p3PacketsTx": link_info["p3PacketsTx"],
                    "controlBytesRx": link_info["controlBytesRx"],
                    "controlBytesTx": link_info["controlBytesTx"],
                    "controlPacketsRx": link_info["controlPacketsRx"],
                    "controlPacketsTx": link_info["controlPacketsTx"],
                    "bpsOfBestPathRx": link_info["bpsOfBestPathRx"],
                    "bpsOfBestPathTx": link_info["bpsOfBestPathTx"],
                    "bestJitterMsRx": link_info["bestJitterMsRx"],
                    "bestJitterMsTx": link_info["bestJitterMsTx"],
                    "bestLatencyMsRx": link_info["bestLatencyMsRx"],
                    "bestLatencyMsTx": link_info["bestLatencyMsTx"],
                    "bestLossPctRx": link_info["bestLossPctRx"],
                    "bestLossPctTx": link_info["bestLossPctTx"],
                    "scoreTx": link_info["scoreTx"],
                    "scoreRx": link_info["scoreRx"],
                    "signalStrength": link_info["signalStrength"],
                    "state": link_info["state"],
                },
            }

            if events is not None:
                serial = structured_link["edge_status"]["edgeSerialNumber"]
                interface = structured_link["link_status"]["interface"]
                structured_link["link_events"] = events[serial][interface]

            result.append(structured_link)

        return result

    def _map_cached_edges_with_links_metrics_and_contact_info(self, links_metrics: list) -> list:
        result = []

        cached_edges_by_serial = {elem["serial_number"]: elem for elem in self._customer_cache}

        for elem in links_metrics:
            serial_number = elem["edge_status"]["edgeSerialNumber"]
            cached_edge = cached_edges_by_serial.get(serial_number)
            if not cached_edge:
                logger.warning(f"No cached info was found for edge {serial_number}. Skipping...")
                continue

            client_id = cached_edge["bruin_client_info"]["client_id"]
            site_details = cached_edge["site_details"]
            ticket_contact_details = cached_edge["ticket_contact_details"]
            ticket_contact_additional_subscribers = cached_edge["ticket_contact_additional_subscribers"]

            default_contacts = self._default_contact_info_by_client_id.get(client_id)
            if self._should_use_default_contact_info(client_id, cached_edge):
                logger.info(f"Using default contact info for edge {serial_number} and client {client_id}")
                contacts = default_contacts
                subscribers = []
            else:
                logger.info(f"Using site and ticket contact info for edge {serial_number} and client {client_id}")
                contacts = (self._bruin_repository.get_contact_info_from_site_and_ticket_contact_details(
                    site_details, ticket_contact_details) or default_contacts)
                subscribers = self._bruin_repository.get_ticket_contact_additional_subscribers(
                    ticket_contact_additional_subscribers)

            result.append(
                {
                    "cached_info": cached_edge,
                    "contact_info": contacts,
                    "subscribers": subscribers,
                    **elem,
                }
            )

        return result

    async def _run_autoresolve_process(self):
        logger.info("Starting auto-resolve process...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_autoresolve()
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            logger.warning("List of links metrics arrived empty while running auto-resolve process. Skipping...")
            return

        events = await self._velocloud_repository.get_events_by_serial_and_interface(self._customer_cache)
        links_metrics = self._structure_links_metrics(links_metrics, events)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics
        )
        edges_with_links_info = self._group_links_by_edge(metrics_with_cache_and_contact_info)

        logger.info(f"Running auto-resolve for {len(edges_with_links_info)} edges")
        autoresolve_tasks = [self._run_autoresolve_for_edge(edge) for edge in edges_with_links_info]
        await asyncio.gather(*autoresolve_tasks)

        logger.info("Auto-resolve process finished!")

    async def _run_autoresolve_for_edge(self, edge: dict):
        async with self.__autoresolve_semaphore:
            serial_number = edge["cached_info"]["serial_number"]
            client_id = edge["cached_info"]["bruin_client_info"]["client_id"]
            client_name = edge["cached_info"]["bruin_client_info"]["client_name"]
            links_configuration = edge["cached_info"]["links_configuration"]
            logical_ids = edge["cached_info"]["logical_ids"]
            host = edge["cached_info"]["edge"]["host"]

            logger.info(f"Starting autoresolve for edge {serial_number}...")

            check_bandwidth_troubles = self._trouble_repository.should_check_bandwidth_troubles(host, client_id)
            metrics_lookup_interval = self._config.MONITOR_CONFIG["autoresolve"]["metrics_lookup_interval_minutes"]
            all_metrics_within_thresholds = self._trouble_repository.are_all_metrics_within_thresholds(
                edge,
                lookup_interval_minutes=metrics_lookup_interval,
                check_bandwidth_troubles=check_bandwidth_troubles,
                links_configuration=links_configuration,
            )
            if not all_metrics_within_thresholds:
                logger.warning(
                    f"At least one metric of edge {serial_number} is not within the threshold. Skipping autoresolve..."
                )
                return

            affecting_ticket_response = await self._bruin_repository.get_open_affecting_tickets(
                client_id, service_number=serial_number
            )
            affecting_ticket_response_status = affecting_ticket_response["status"]
            if affecting_ticket_response_status not in range(200, 300):
                logger.error(
                    f"Error while getting open Service Affecting tickets for edge {serial_number}: "
                    f"{affecting_ticket_response}. Skipping autoresolve..."
                )
                return

            affecting_tickets: list = affecting_ticket_response["body"]
            if not affecting_tickets:
                logger.warning(
                    f"No affecting ticket found for edge with serial number {serial_number}. Skipping autoresolve..."
                )
                return

            for affecting_ticket in affecting_tickets:
                affecting_ticket_id = affecting_ticket["ticketID"]
                affecting_ticket_creation_date = affecting_ticket["createDate"]

                if not self._ticket_repository.was_ticket_created_by_automation_engine(affecting_ticket):
                    logger.warning(
                        f"Ticket {affecting_ticket_id} was not created by Automation Engine. Skipping autoresolve..."
                    )
                    continue

                ticket_details_response = await self._bruin_repository.get_ticket_details(affecting_ticket_id)
                ticket_details_response_body = ticket_details_response["body"]
                ticket_details_response_status = ticket_details_response["status"]
                if ticket_details_response_status not in range(200, 300):
                    logger.error(
                        f"Error while getting details of ticket {affecting_ticket_id}: "
                        f"{ticket_details_response}. Skipping autoresolve..."
                    )
                    continue

                details_from_ticket = ticket_details_response_body["ticketDetails"]
                detail_for_ticket_resolution = self._ticket_repository.find_task_by_serial_number(
                    details_from_ticket, serial_number
                )
                ticket_detail_id = detail_for_ticket_resolution["detailID"]

                notes_from_affecting_ticket = ticket_details_response_body["ticketNotes"]
                relevant_notes = [
                    note
                    for note in notes_from_affecting_ticket
                    if note["serviceNumber"] is not None
                    if serial_number in note["serviceNumber"]
                    if note["noteValue"] is not None
                ]

                last_cycle_notes = self._ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(
                    relevant_notes
                )
                affecting_trouble_note = self._ticket_repository.get_affecting_trouble_note(last_cycle_notes)
                troubles = self._get_troubles_from_ticket_notes(last_cycle_notes)
                is_byob = self._get_is_byob_from_affecting_trouble_note(affecting_trouble_note)
                link_type = self._get_link_type_from_affecting_trouble_note(affecting_trouble_note)
                link_access_type = self._get_link_access_type_from_affecting_trouble_note(
                    affecting_trouble_note, logical_ids)

                max_seconds_since_last_trouble = self._get_max_seconds_since_last_trouble(edge)
                last_trouble_was_detected_recently = self._trouble_repository.was_last_trouble_detected_recently(
                    relevant_notes,
                    affecting_ticket_creation_date,
                    max_seconds_since_last_trouble=max_seconds_since_last_trouble,
                )

                is_task_in_ipa_queue = self._ticket_repository.is_ticket_task_in_ipa_queue(detail_for_ticket_resolution)
                is_task_assigned = self._ticket_repository.is_ticket_task_assigned(detail_for_ticket_resolution)
                if is_byob and is_task_in_ipa_queue:
                    logger.info(
                        f"Task for serial {serial_number} in ticket {affecting_ticket_id} is related to a BYOB link "
                        f"and is in the IPA Investigate queue. Ignoring auto-resolution restrictions..."
                    )
                elif link_access_type == "Ethernet/T1/MPLS" and is_task_assigned:
                    logger.info(
                        f"Task for serial {serial_number} in ticket {affecting_ticket_id} is related to an Ethernet"
                        f" link and is assigned. Ignoring auto-resolution..."
                    )
                    continue
                else:
                    if not last_trouble_was_detected_recently:
                        logger.warning(
                            f"Edge with serial number {serial_number} has been under an affecting trouble for a long "
                            f"time, so the detail of ticket {affecting_ticket_id} related to it will not be "
                            f"autoresolved. Skipping autoresolve..."
                        )
                        continue

                    if self._ticket_repository.is_autoresolve_threshold_maxed_out(relevant_notes):
                        logger.warning(
                            f"Limit to autoresolve detail of ticket {affecting_ticket_id} related to serial "
                            f"{serial_number} has been maxed out already. Skipping autoresolve..."
                        )
                        continue

                if self._ticket_repository.is_task_resolved(detail_for_ticket_resolution):
                    logger.warning(
                        f"Detail of ticket {affecting_ticket_id} related to serial {serial_number} is already "
                        "resolved. Skipping autoresolve..."
                    )
                    continue

                working_environment = self._config.CURRENT_ENVIRONMENT
                if working_environment != "production":
                    logger.info(
                        f"Skipping autoresolve for detail of ticket {affecting_ticket_id} related to serial number "
                        f"{serial_number} since the current environment is {working_environment.upper()}"
                    )
                    continue

                logger.info(
                    f"Autoresolving detail of ticket {affecting_ticket_id} related to serial number {serial_number}..."
                )
                await self._bruin_repository.unpause_ticket_detail(affecting_ticket_id, serial_number)
                resolve_ticket_response = await self._bruin_repository.resolve_ticket(
                    affecting_ticket_id, ticket_detail_id
                )
                if resolve_ticket_response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while resolving ticket task of ticket {affecting_ticket_id} for edge {serial_number}: "
                        f"{resolve_ticket_response}. Skipping autoresolve..."
                    )
                    continue

                self._metrics_repository.increment_tasks_autoresolved(
                    client=client_name, troubles=troubles, has_byob=is_byob, link_type=link_type
                )
                await self._bruin_repository.append_autoresolve_note_to_ticket(affecting_ticket_id, serial_number)
                await self._notifications_repository.notify_successful_autoresolve(affecting_ticket_id, serial_number)

                logger.info(
                    f"Detail of ticket {affecting_ticket_id} related to serial number {serial_number} was autoresolved!"
                )

                task_type = TaskTypes.TICKET_FORWARDS
                task_key = f"{affecting_ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

                if self._task_dispatcher_client.clear_task(task_type, task_key):
                    logger.info(
                        f"Removed scheduled task to forward to {ForwardQueues.HNOC.value} "
                        f"for autoresolved ticket {affecting_ticket_id} and serial number {serial_number}"
                    )

            logger.info(f"Finished autoresolve for edge {serial_number}!")

    @staticmethod
    def _group_links_by_edge(links: List[dict]) -> List[dict]:
        edge_info_by_serial = {}

        for link in links:
            serial_number = link["cached_info"]["serial_number"]

            edge_info = {
                "cached_info": link["cached_info"],
                "contact_info": link["contact_info"],
                "edge_status": link["edge_status"],
                "links": [],
            }
            edge_info_by_serial.setdefault(serial_number, edge_info)

            link_info = {
                "link_status": link["link_status"],
                "link_metrics": link["link_metrics"],
                "link_events": link["link_events"],
            }
            edge_info_by_serial[serial_number]["links"].append(link_info)

        return list(edge_info_by_serial.values())

    async def _latency_check(self, for_wireless: bool):
        logger.info(f"Looking for latency issues (for_wireless={for_wireless})...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_latency_checks(
            for_wireless=for_wireless
        )
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            logger.warning("List of links arrived empty while checking latency issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics
        )

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]
            interface = link_status["interface"]
            links_configuration = cached_info["links_configuration"]

            is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

            serial_number = cached_info["serial_number"]

            if (is_wireless_link and not for_wireless) or (not is_wireless_link and for_wireless):
                continue

            if self._trouble_repository.are_latency_metrics_within_threshold(metrics, is_wireless_link):
                logger.info(f"Link {interface} from {serial_number} didn't exceed latency thresholds")
                continue

            await self._process_latency_trouble(elem)

        logger.info("Finished looking for latency issues!")

    async def _packet_loss_check(self, for_wireless: bool):
        logger.info(f"Looking for packet loss issues (for_wireless={for_wireless})...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_packet_loss_checks(
            for_wireless=for_wireless
        )
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            logger.warning("List of links arrived empty while checking packet loss issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics
        )

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]
            interface = link_status["interface"]
            links_configuration = cached_info["links_configuration"]

            is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

            serial_number = cached_info["serial_number"]

            if (is_wireless_link and not for_wireless) or (not is_wireless_link and for_wireless):
                continue

            if self._trouble_repository.are_packet_loss_metrics_within_threshold(metrics, is_wireless_link):
                logger.info(
                    f"Link {interface} from {serial_number} didn't exceed packet loss thresholds"
                )
                continue

            await self._process_packet_loss_trouble(elem)

        logger.info("Finished looking for packet loss issues!")

    async def _jitter_check(self, for_wireless: bool):
        logger.info(f"Looking for jitter issues (for_wireless={for_wireless})...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_jitter_checks(
            for_wireless=for_wireless
        )
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            logger.warning("List of links arrived empty while checking jitter issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics
        )

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]
            interface = link_status["interface"]
            links_configuration = cached_info["links_configuration"]

            is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

            serial_number = cached_info["serial_number"]

            if (is_wireless_link and not for_wireless) or (not is_wireless_link and for_wireless):
                continue

            if self._trouble_repository.are_jitter_metrics_within_threshold(metrics, is_wireless_link):
                logger.info(f"Link {interface} from {serial_number} didn't exceed jitter thresholds")
                continue

            await self._process_jitter_trouble(elem)

        logger.info("Finished looking for jitter issues!")

    async def _bandwidth_check(self, for_wireless: bool):
        logger.info(f"Looking for bandwidth issues (for_wireless={for_wireless})...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bandwidth_checks(
            for_wireless=for_wireless
        )
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            logger.warning("List of links arrived empty while checking bandwidth issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics
        )

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            client_id = cached_info["bruin_client_info"]["client_id"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]
            host = cached_info["edge"]["host"]
            interface = link_status["interface"]
            links_configuration = cached_info["links_configuration"]

            is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

            if (is_wireless_link and not for_wireless) or (not is_wireless_link and for_wireless):
                continue

            if not self._trouble_repository.should_check_bandwidth_troubles(host, client_id):
                logger.warning(f"Bandwidth checks are not enabled for host {host}, or client {client_id}. Skipping...")
                continue

            tx_bandwidth = metrics["bpsOfBestPathTx"]
            rx_bandwidth = metrics["bpsOfBestPathRx"]

            is_tx_bandwidth_valid = self._trouble_repository.is_valid_bps_metric(tx_bandwidth)
            is_rx_bandwidth_valid = self._trouble_repository.is_valid_bps_metric(rx_bandwidth)

            serial_number = cached_info["serial_number"]

            trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
            monitoring_minutes_per_trouble = self._utils_repository.monitoring_minutes_per_trouble_metric_to_use(
                is_wireless_link)
            scan_interval = self._config.MONITOR_CONFIG[monitoring_minutes_per_trouble][trouble]

            if is_tx_bandwidth_valid and is_rx_bandwidth_valid:
                within_threshold = self._trouble_repository.are_bandwidth_metrics_within_threshold(
                    metrics, scan_interval, is_wireless_link
                )
            elif is_tx_bandwidth_valid and not is_rx_bandwidth_valid:
                within_threshold = self._trouble_repository.is_bandwidth_tx_within_threshold(
                    metrics, scan_interval, is_wireless_link)
            elif is_rx_bandwidth_valid and not is_tx_bandwidth_valid:
                within_threshold = self._trouble_repository.is_bandwidth_rx_within_threshold(
                    metrics, scan_interval, is_wireless_link)
            else:
                continue

            if within_threshold:
                logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed any bandwidth thresholds"
                )
                continue

            await self._process_bandwidth_trouble(elem)

        logger.info("Finished looking for bandwidth issues!")

    async def _bouncing_check(self, for_wireless: bool):
        logger.info(f"Looking for bouncing issues (for_wireless={for_wireless})...")

        if for_wireless:
            logger.info("Skipping bouncing check for wireless links")
            return

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bouncing_checks(
            for_wireless=for_wireless
        )
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            logger.warning("List of links arrived empty while checking bouncing issues. Skipping...")
            return

        events = await self._velocloud_repository.get_events_by_serial_and_interface(
            self._customer_cache, for_wireless
        )
        links_metrics = self._structure_links_metrics(links_metrics, events)
        metrics_with_cache_and_contact_info = self._map_cached_edges_with_links_metrics_and_contact_info(
            links_metrics
        )

        for elem in metrics_with_cache_and_contact_info:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            events = elem["link_events"]
            interface = link_status["interface"]
            links_configuration = cached_info["links_configuration"]

            is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

            serial_number = cached_info["serial_number"]

            if not events:
                logger.warning(
                    f"No events were found for {link_status['interface']} from {serial_number} "
                    f"while looking for bouncing troubles"
                )
                continue

            if self._trouble_repository.are_bouncing_events_within_threshold(events, is_wireless_link):
                logger.info(f"Link {link_status['interface']} from {serial_number} didn't exceed bouncing thresholds")
                continue

            await self._process_bouncing_trouble(elem)

        logger.info("Finished looking for bouncing issues!")

    async def _process_latency_trouble(self, link_data: dict):
        trouble = AffectingTroubles.LATENCY
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_packet_loss_trouble(self, link_data: dict):
        trouble = AffectingTroubles.PACKET_LOSS
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_jitter_trouble(self, link_data: dict):
        trouble = AffectingTroubles.JITTER
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_bandwidth_trouble(self, link_data: dict):
        trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_bouncing_trouble(self, link_data: dict):
        trouble = AffectingTroubles.BOUNCING
        ticket_id = await self._process_affecting_trouble(link_data, trouble)
        await self._attempt_forward_to_asr(link_data, trouble, ticket_id)

    async def _process_affecting_trouble(self, link_data: dict, trouble: AffectingTroubles) -> Optional[int]:
        trouble_processed = False
        resolved_affecting_ticket = None
        ticket_id = None

        serial_number = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]
        client_id = link_data["cached_info"]["bruin_client_info"]["client_id"]
        link_label = link_data["link_status"]["displayName"]

        is_byob = self._is_link_label_blacklisted_from_hnoc(link_label)

        logger.info(
            f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
            f"{serial_number}"
        )

        if is_byob:
            logger.warning(
                f"Link blacklisted as BYOB. Interface {interface} of edge {serial_number}"
            )
            return

        open_affecting_tickets_response = await self._bruin_repository.get_open_affecting_tickets(
            client_id, service_number=serial_number
        )
        if open_affecting_tickets_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting open Service Affecting tickets for edge {serial_number}: "
                f"{open_affecting_tickets_response}. Skipping processing Service Affecting trouble..."
            )
            return

        # Get oldest open ticket related to Service Affecting Monitor (i.e. trouble must be latency, packet loss, jitter
        # or bandwidth)
        open_affecting_tickets = open_affecting_tickets_response["body"]
        open_affecting_ticket = await self._get_oldest_affecting_ticket_for_serial_number(
            open_affecting_tickets, serial_number
        )

        if open_affecting_ticket:
            ticket_id = open_affecting_ticket["ticket_overview"]["ticketID"]
            logger.info(f"An open Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}")

            # The task related to the serial we're checking can be in Resolved state, even if the ticket is returned as
            # open by Bruin. If that's the case, the task should be re-opened instead.
            if self._ticket_repository.is_task_resolved(open_affecting_ticket["ticket_task"]):
                logger.info(
                    f"Service Affecting ticket with ID {ticket_id} is open, but the task related to edge "
                    f"{serial_number} is Resolved. Therefore, the ticket will be considered as Resolved."
                )
                resolved_affecting_ticket = {**open_affecting_ticket}
                open_affecting_ticket = None
            else:
                await self._append_latest_trouble_to_ticket(open_affecting_ticket, trouble, link_data)
                trouble_processed = True

                link_label = link_data["link_status"]["displayName"]
                if not self._should_forward_to_hnoc(link_label):
                    await self._send_reminder(open_affecting_ticket)
        else:
            logger.info(f"No open Service Affecting ticket was found for edge {serial_number}")

        # If we didn't get a Resolved ticket in the Open Tickets flow, we need to go look for it
        if not trouble_processed and not resolved_affecting_ticket:
            resolved_affecting_tickets_response = await self._bruin_repository.get_resolved_affecting_tickets(
                client_id, service_number=serial_number
            )
            if resolved_affecting_tickets_response["status"] not in range(200, 300):
                logger.error(
                    f"Error while getting resolved Service Affecting tickets for edge {serial_number}: "
                    f"{resolved_affecting_tickets_response}. Skipping processing Service Affecting trouble..."
                )
                return

            resolved_affecting_tickets = resolved_affecting_tickets_response["body"]
            resolved_affecting_ticket = await self._get_oldest_affecting_ticket_for_serial_number(
                resolved_affecting_tickets, serial_number
            )

        # If any of Open Ticket or Resolved Tickets flows returned a Resolved ticket task, keep going
        if not trouble_processed and resolved_affecting_ticket:
            ticket_id = resolved_affecting_ticket["ticket_overview"]["ticketID"]
            logger.info(
                f"A resolved Service Affecting ticket was found for edge {serial_number}. Ticket ID: {ticket_id}"
            )
            await self._unresolve_task_for_affecting_ticket(resolved_affecting_ticket, trouble, link_data)
            trouble_processed = True
        else:
            logger.info(f"No resolved Service Affecting ticket was found for edge {serial_number}")

        # If not a single ticket was found for the serial, create a new one
        if not trouble_processed and not open_affecting_ticket and not resolved_affecting_ticket:
            logger.info(f"No open or resolved Service Affecting ticket was found for edge {serial_number}")
            ticket_id = await self._create_affecting_ticket(trouble, link_data)

        logger.info(
            f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
            f"{serial_number} has been processed"
        )

        return ticket_id

    async def _get_oldest_affecting_ticket_for_serial_number(
        self, tickets: List[dict], serial_number: str
    ) -> Optional[dict]:
        tickets = sorted(tickets, key=lambda item: parse(item["createDate"]))

        for ticket in tickets:
            ticket_id = ticket["ticketID"]
            ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)

            if ticket_details_response["status"] not in range(200, 300):
                logger.error(
                    f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
                    f"The oldest Service Affecting ticket cannot be determined."
                )
                return

            ticket_notes = ticket_details_response["body"]["ticketNotes"]
            relevant_notes = [
                note
                for note in ticket_notes
                if note["serviceNumber"] is not None
                if serial_number in note["serviceNumber"]
                if note["noteValue"] is not None
            ]

            if not self._ticket_repository.is_ticket_used_for_reoccurring_affecting_troubles(relevant_notes):
                logger.info(
                    f"Ticket {ticket_id} linked to edge {serial_number} is not being actively used to report "
                    f"Service Affecting troubles"
                )
                continue

            ticket_tasks = ticket_details_response["body"]["ticketDetails"]
            relevant_task = self._ticket_repository.find_task_by_serial_number(ticket_tasks, serial_number)
            return {
                "ticket_overview": ticket,
                "ticket_task": relevant_task,
                "ticket_notes": relevant_notes,
            }

    async def _append_latest_trouble_to_ticket(self, ticket_info: dict, trouble: AffectingTroubles, link_data: dict):
        ticket_id = ticket_info["ticket_overview"]["ticketID"]
        serial_number = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]
        links_configuration = link_data["cached_info"]["links_configuration"]

        is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

        logger.info(
            f"Appending Service Affecting trouble note to ticket {ticket_id} for {trouble.value} trouble detected in "
            f"interface {interface} of edge {serial_number}..."
        )

        ticket_id = ticket_info["ticket_overview"]["ticketID"]
        ticket_notes = ticket_info["ticket_notes"]

        # Get notes since latest re-open or ticket creation
        filtered_notes = self._ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(ticket_notes)

        # If there is a SA trouble note for the current trouble since the latest re-open note, skip
        # Otherwise, append SA trouble note to ticket using the callback passed as parameter
        if self._ticket_repository.is_there_any_note_for_trouble(filtered_notes, trouble):
            logger.info(
                f"No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble "
                f"detected in interface {interface} of edge {serial_number}. A note for this trouble was already "
                f"appended to the ticket after the latest re-open (or ticket creation)"
            )
            return

        build_note_fn = self._ticket_repository.get_build_note_fn_by_trouble(trouble)
        affecting_trouble_note = build_note_fn(link_data, is_wireless_link)

        working_environment = self._config.CURRENT_ENVIRONMENT
        if not working_environment == "production":
            logger.info(
                f"No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble "
                f"detected in interface {interface} of edge {serial_number}, since the current environment is "
                f"{working_environment.upper()}"
            )
            return

        append_note_response = await self._bruin_repository.append_note_to_ticket(
            ticket_id,
            affecting_trouble_note,
            service_numbers=[serial_number],
        )
        if append_note_response["status"] not in range(200, 300):
            logger.error(
                f"Error while appending latest trouble for edge {serial_number} as a note to ticket {ticket_id}: "
                f"{append_note_response}"
            )
            return

        logger.info(
            f"Service Affecting trouble note for {trouble.value} trouble detected in interface {interface} "
            f"of edge {serial_number} was successfully appended to ticket {ticket_id}!"
        )
        await self._notifications_repository.notify_successful_note_append(ticket_id, serial_number, trouble)

    async def _unresolve_task_for_affecting_ticket(
        self, ticket_info: dict, trouble: AffectingTroubles, link_data: dict
    ):
        ticket_id = ticket_info["ticket_overview"]["ticketID"]
        serial_number = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]
        client_name = link_data["cached_info"]["bruin_client_info"]["client_name"]
        link_label = link_data["link_status"]["displayName"]
        links_configuration = link_data["cached_info"]["links_configuration"]

        is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

        is_byob = self._is_link_label_blacklisted_from_hnoc(link_label)
        link_type = self._get_link_type(interface, links_configuration)

        logger.info(
            f"Unresolving task related to edge {serial_number} of Service Affecting ticket {ticket_id} due to a "
            f"{trouble.value} trouble detected in interface {interface}..."
        )

        ticket_id = ticket_info["ticket_overview"]["ticketID"]
        task_id = ticket_info["ticket_task"]["detailID"]

        working_environment = self._config.CURRENT_ENVIRONMENT
        if not working_environment == "production":
            logger.info(
                f"Task related to edge {serial_number} of Service Affecting ticket {ticket_id} will not be unresolved "
                f"because of the {trouble.value} trouble detected in interface {interface}, since the current "
                f"environment is {working_environment.upper()}"
            )
            return

        unresolve_task_response = await self._bruin_repository.open_ticket(ticket_id, task_id)
        if unresolve_task_response["status"] not in range(200, 300):
            logger.error(
                f"Error while unresolving Service Affecting ticket task for edge {serial_number}: "
                f"{unresolve_task_response}"
            )
            return

        logger.info(
            f"Task related to edge {serial_number} of Service Affecting ticket {ticket_id} was successfully "
            f"unresolved! The cause was a {trouble.value} trouble detected in interface {interface}"
        )

        self._metrics_repository.increment_tasks_reopened(
            client=client_name, trouble=trouble.value, has_byob=is_byob, link_type=link_type
        )
        await self._notifications_repository.notify_successful_reopen(ticket_id, serial_number, trouble)

        build_note_fn = self._ticket_repository.get_build_note_fn_by_trouble(trouble)
        reopen_trouble_note = build_note_fn(link_data, is_wireless_link, is_reopen_note=True)
        await self._bruin_repository.append_note_to_ticket(
            ticket_id,
            reopen_trouble_note,
            service_numbers=[serial_number],
        )

        link_label = link_data["link_status"]["displayName"]
        if self._should_forward_to_hnoc(link_label):
            forward_time = self._get_max_seconds_since_last_trouble(link_data) / 60
            logger.info(
                f"Forwarding reopened task for serial {serial_number} of ticket {ticket_id} to the HNOC queue..."
            )
            self._schedule_forward_to_hnoc_queue(forward_time, ticket_id, serial_number, link_data, trouble)
        else:
            logger.info(
                f"Ticket_id: {ticket_id} for serial: {serial_number} with link_label: "
                f"{link_data['link_status']['displayName']} is a blacklisted link and "
                f"should not be forwarded to HNOC. Skipping forward to HNOC..."
            )

            logger.info(
                f"Sending an email for the reopened task of ticket_id: {ticket_id} "
                f"with serial: {serial_number} instead of scheduling forward to HNOC..."
            )
            email_response = await self._bruin_repository.send_initial_email_milestone_notification(
                ticket_id, serial_number
            )
            if email_response["status"] not in range(200, 300):
                logger.error(f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!")
                return

            append_note_response = await self._append_reminder_note(ticket_id, serial_number)
            if append_note_response["status"] not in range(200, 300):
                logger.error(f"Reminder note of edge {serial_number} could not be appended to ticket {ticket_id}!")
                return

    async def _create_affecting_ticket(self, trouble: AffectingTroubles, link_data: dict) -> Optional[int]:
        serial_number = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]
        client_id = link_data["cached_info"]["bruin_client_info"]["client_id"]
        contact_info = link_data["contact_info"]
        subscribers = link_data["subscribers"]
        client_name = link_data["cached_info"]["bruin_client_info"]["client_name"]
        link_label = link_data["link_status"]["displayName"]
        links_configuration = link_data["cached_info"]["links_configuration"]

        is_wireless_link = self._utils_repository.get_is_wireless_link(interface, links_configuration)

        is_byob = self._is_link_label_blacklisted_from_hnoc(link_label)
        link_type = self._get_link_type(interface, links_configuration)

        logger.info(
            f"Creating Service Affecting ticket to report a {trouble.value} trouble detected in interface {interface} "
            f"of edge {serial_number}..."
        )

        working_environment = self._config.CURRENT_ENVIRONMENT
        if not working_environment == "production":
            logger.info(
                f"No Service Affecting ticket will be created to report a {trouble.value} trouble detected in "
                f"interface {interface} of edge {serial_number}, since the current environment is "
                f"{working_environment.upper()}"
            )
            return

        create_affecting_ticket_response = await self._bruin_repository.create_affecting_ticket(
            client_id, serial_number, contact_info
        )
        if create_affecting_ticket_response["status"] not in range(200, 300):
            logger.error(
                f"Error while creating Service Affecting ticket for edge {serial_number}: "
                f"{create_affecting_ticket_response}. Skipping ticket creation..."
            )
            return

        ticket_id = create_affecting_ticket_response["body"]["ticketIds"][0]
        logger.info(
            f"Service Affecting ticket to report {trouble.value} trouble detected in interface {interface} "
            f"of edge {serial_number} was successfully created! Ticket ID is {ticket_id}"
        )

        if subscribers:
            for subscriber in subscribers:
                subscriber_user_response = await self._bruin_repository.subscribe_user_to_ticket(ticket_id, subscriber)
                if subscriber_user_response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while subscribing {subscriber} to ticket {ticket_id}: {subscriber_user_response}.")

        self._metrics_repository.increment_tasks_created(
            client=client_name, trouble=trouble.value, has_byob=is_byob, link_type=link_type
        )
        await self._notifications_repository.notify_successful_ticket_creation(ticket_id, serial_number, trouble)

        build_note_fn = self._ticket_repository.get_build_note_fn_by_trouble(trouble)
        affecting_trouble_note = build_note_fn(link_data, is_wireless_link)

        await self._bruin_repository.append_note_to_ticket(
            ticket_id,
            affecting_trouble_note,
            service_numbers=[serial_number],
        )

        link_label = link_data["link_status"]["displayName"]
        if trouble is not AffectingTroubles.BOUNCING:
            if self._should_forward_to_hnoc(link_label):
                forward_time = self._get_max_seconds_since_last_trouble(link_data) / 60
                self._schedule_forward_to_hnoc_queue(forward_time, ticket_id, serial_number, link_data, trouble)
            else:
                logger.info(
                    f"Ticket_id: {ticket_id} for serial: {serial_number} with link_label: "
                    f"{link_data['link_status']['displayName']} is a blacklisted link and "
                    f"should not be forwarded to HNOC. Skipping forward to HNOC..."
                )

                logger.info(
                    f"Sending an email for ticket_id: {ticket_id} "
                    f"with serial: {serial_number} instead of scheduling forward to HNOC..."
                )
                email_response = await self._bruin_repository.send_initial_email_milestone_notification(
                    ticket_id, serial_number
                )
                if email_response["status"] not in range(200, 300):
                    logger.error(f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!")
                    return

                append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                if append_note_response["status"] not in range(200, 300):
                    logger.error(f"Reminder note of edge {serial_number} could not be appended to ticket {ticket_id}!")
                    return

        return ticket_id

    def _should_forward_to_hnoc(self, link_label: str) -> bool:
        return not self._is_link_label_blacklisted_from_hnoc(link_label)

    def _schedule_forward_to_hnoc_queue(self, forward_time, ticket_id, serial_number, link_data, trouble):
        target_queue = ForwardQueues.HNOC
        current_datetime = datetime.utcnow()
        forward_task_run_date = current_datetime + timedelta(minutes=forward_time)

        interface = link_data["link_status"]["interface"]
        client_name = link_data["cached_info"]["bruin_client_info"]["client_name"]
        link_label = link_data["link_status"]["displayName"]
        links_configuration = link_data["cached_info"]["links_configuration"]

        is_byob = self._is_link_label_blacklisted_from_hnoc(link_label)
        link_type = self._get_link_type(interface, links_configuration)

        logger.info(
            f"Scheduling forward to {target_queue.value} for ticket {ticket_id} and serial number {serial_number} "
            f"to happen in {forward_time} minutes"
        )

        self._task_dispatcher_client.schedule_task(
            date=forward_task_run_date,
            task_type=TaskTypes.TICKET_FORWARDS,
            task_key=f"{ticket_id}-{serial_number}-{target_queue.name}",
            task_data={
                "service": self._config.LOG_CONFIG["name"],
                "ticket_id": ticket_id,
                "serial_number": serial_number,
                "target_queue": target_queue.value,
                "metrics_labels": {
                    "client": client_name,
                    "trouble": trouble.value,
                    "has_byob": is_byob,
                    "link_type": link_type,
                    "target_queue": target_queue.value,
                },
            },
        )

    async def _attempt_forward_to_asr(self, link_data: dict, trouble: AffectingTroubles, ticket_id: Optional[int]):
        serial_number = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]

        if not ticket_id:
            logger.warning(
                f"No ticket could be created, re-opened or updated for edge {serial_number} and link {interface}. "
                f"Skipping forward to ASR..."
            )
            return

        logger.info(
            f"Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate..."
        )

        target_queue = ForwardQueues.ASR.value
        links_configuration = link_data["cached_info"]["links_configuration"]
        client_name = link_data["cached_info"]["bruin_client_info"]["client_name"]
        link_label = link_data["link_status"]["displayName"]
        link_interface_type = ""

        is_byob = self._is_link_label_blacklisted_from_hnoc(link_label)
        link_type = self._get_link_type(interface, links_configuration)

        for link_configuration in links_configuration:
            if interface in link_configuration["interfaces"]:
                link_interface_type = link_configuration["type"]

        if link_interface_type != "WIRED" and self._should_forward_to_hnoc(link_label):
            forward_time = 0
            logger.warning(
                f"Link {interface} is of type {link_interface_type} and not WIRED. Attempting to forward to HNOC..."
            )
            self._schedule_forward_to_hnoc_queue(forward_time, ticket_id, serial_number, link_data, trouble)
            return

        logger.info(
            f"Filtering out any of the wired links of serial {serial_number} that contains any of the following: "
            f"{self._config.MONITOR_CONFIG['blacklisted_link_labels_for_asr_forwards']} in the link label"
        )

        if not self._should_forward_to_asr(link_data):
            logger.warning(
                f"No links with whitelisted labels were found for serial {serial_number}. "
                f"Related detail of ticket {ticket_id} will not be forwarded to {target_queue}."
            )
            return

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response["body"]
        ticket_details_response_status = ticket_details_response["status"]
        if ticket_details_response_status not in range(200, 300):
            logger.error(
                f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. Skipping autoresolve..."
            )
            return

        details_from_ticket = ticket_details_response_body["ticketDetails"]
        ticket_details = self._utils_repository.get_first_element_matching(
            details_from_ticket,
            lambda detail: detail["detailValue"] == serial_number,
        )

        notes_from_outage_ticket = ticket_details_response_body["ticketNotes"]

        ticket_notes = [
            note
            for note in notes_from_outage_ticket
            if note["serviceNumber"] is not None
            if serial_number in note["serviceNumber"]
            if note["noteValue"] is not None
        ]
        ticket_detail_id = ticket_details["detailID"]

        other_troubles_in_ticket = self._ticket_repository.are_there_any_other_troubles(
            ticket_notes, AffectingTroubles.BOUNCING
        )

        if other_troubles_in_ticket:
            logger.warning(
                f"Other service affecting troubles were found in ticket id {ticket_id}. Skipping forward to ASR..."
            )
            return

        task_result = "No Trouble Found - Carrier Issue"
        task_result_note = self._utils_repository.get_first_element_matching(
            ticket_notes, lambda note: target_queue in note.get("noteValue")
        )

        if task_result_note is not None:
            logger.warning(
                f"Detail related to serial {serial_number} of ticket {ticket_id} has already been forwarded to "
                f'"{task_result}"'
            )
            return

        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            ticket_id, task_result, service_number=serial_number, detail_id=ticket_detail_id
        )
        if change_detail_work_queue_response["status"] in range(200, 300):
            self._metrics_repository.increment_tasks_forwarded(
                client=client_name,
                trouble=trouble.value,
                has_byob=is_byob,
                link_type=link_type,
                target_queue=target_queue,
            )
            await self._bruin_repository.append_asr_forwarding_note(ticket_id, link_data["link_status"], serial_number)
            slack_message = (
                f"Detail of Circuit Instability ticket {ticket_id} related to serial {serial_number} "
                f"was successfully forwarded to {task_result} queue!"
            )
            await self._notifications_repository.send_slack_message(slack_message)

    def _should_forward_to_asr(self, link_data: dict) -> bool:
        link_label = link_data["link_status"]["displayName"]
        is_blacklisted = self._is_link_label_blacklisted_from_asr(link_label)
        is_ip_address = self._utils_repository.is_ip_address(link_label)
        return not is_blacklisted and not is_ip_address

    @staticmethod
    def _is_link_label_blacklisted(link_label: str, blacklisted_link_labels: List[str]) -> bool:
        if not link_label:
            return False
        return any(label for label in blacklisted_link_labels if label.lower() in link_label.lower())

    def _is_link_label_blacklisted_from_asr(self, link_label: str):
        blacklisted_link_labels = self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]
        return self._is_link_label_blacklisted(link_label, blacklisted_link_labels)

    def _is_link_label_blacklisted_from_hnoc(self, link_label: str):
        blacklisted_link_labels = self._config.MONITOR_CONFIG["blacklisted_link_labels_for_hnoc_forwards"]
        return self._is_link_label_blacklisted(link_label, blacklisted_link_labels)

    @staticmethod
    def _get_link_type(interface: str, links_configuration: List[dict]) -> str:
        for link_configuration in links_configuration:
            if interface in link_configuration["interfaces"]:
                return link_configuration["type"]

    @staticmethod
    def _get_troubles_from_ticket_notes(ticket_notes: List[dict]) -> List[AffectingTroubles]:
        troubles = set()

        for note in ticket_notes:
            match = AFFECTING_NOTE_REGEX.search(note["noteValue"])

            if match:
                trouble = match.group("trouble")
                troubles.add(AffectingTroubles(trouble))

        return list(troubles)

    def _get_is_byob_from_affecting_trouble_note(self, affecting_trouble_note: Optional[dict]) -> Optional[bool]:
        if not affecting_trouble_note:
            return None

        match = LINK_INFO_REGEX.search(affecting_trouble_note["noteValue"])

        if match:
            link_label = match.group("label")
            return self._is_link_label_blacklisted_from_hnoc(link_label)

    def _get_link_access_type_from_affecting_trouble_note(
        self, affecting_trouble_note: Optional[dict], logical_id_list: List[dict]
    ) -> Optional[str]:
        if not affecting_trouble_note:
            return None

        match = LINK_INFO_REGEX.search(affecting_trouble_note["noteValue"])

        if match:
            link_label = match.group("interface")
            link_access_type = [
                logical_id["access_type"]
                for logical_id in logical_id_list
                if logical_id["interface_name"] == link_label
            ]
            if link_access_type:
                return link_access_type[0]

    @staticmethod
    def _get_link_type_from_affecting_trouble_note(affecting_trouble_note: Optional[dict]) -> Optional[str]:
        if not affecting_trouble_note:
            return None

        match = LINK_INFO_REGEX.search(affecting_trouble_note["noteValue"])

        if match:
            link_type = match.group("type")
            return link_type

    def _get_max_seconds_since_last_trouble(self, edge: dict) -> int:
        from datetime import timezone

        tz_offset = edge["cached_info"]["site_details"]["tzOffset"]
        tz = timezone(timedelta(hours=tz_offset))
        now = datetime.now(tz=tz)

        last_affecting_trouble_seconds = self._config.MONITOR_CONFIG["autoresolve"]["last_affecting_trouble_seconds"]
        day_schedule = self._config.MONITOR_CONFIG["autoresolve"]["day_schedule"]
        day_start_hour = day_schedule["start_hour"]
        day_end_hour = day_schedule["end_hour"]

        if day_start_hour >= day_end_hour:
            day_end_hour += 24

        if day_start_hour <= now.hour < day_end_hour:
            return last_affecting_trouble_seconds["day"]
        else:
            return last_affecting_trouble_seconds["night"]

    async def _send_reminder(self, ticket: dict):
        ticket_id = ticket["ticket_overview"]["ticketID"]
        service_number = ticket["ticket_task"]["detailValue"]
        logger.info(f"Attempting to send reminder for service number {service_number} to ticket {ticket_id}")

        notes_from_ticket = ticket["ticket_notes"]
        filtered_notes = self._ticket_repository.get_notes_appended_since_latest_reopen_or_ticket_creation(
            notes_from_ticket
        )
        last_documentation_cycle_start_date = (
            filtered_notes[0]["createdDate"] if filtered_notes else ticket["ticket_overview"]["createDate"]
        )

        wait_time_before_sending_new_milestone_reminder = self._config.MONITOR_CONFIG[
            "wait_time_before_sending_new_milestone_reminder"
        ]
        should_send_reminder_notification = not self._was_last_reminder_sent_recently(
            filtered_notes, last_documentation_cycle_start_date, wait_time_before_sending_new_milestone_reminder
        )
        if not should_send_reminder_notification:
            logger.info(
                f"No Reminder note will be appended for service number {service_number} to ticket {ticket_id},"
                f" since either the last documentation cycle started or the last reminder"
                f" was sent too recently"
            )
            return

        working_environment = self._config.CURRENT_ENVIRONMENT
        if not working_environment == "production":
            logger.info(
                f"No Reminder note will be appended for service number {service_number} to ticket {ticket_id} since "
                f"the current environment is {working_environment.upper()}"
            )
            return

        email_response = await self._bruin_repository.send_reminder_email_milestone_notification(
            ticket_id, service_number
        )
        if email_response["status"] not in range(200, 300):
            logger.error(f"Reminder email of edge {service_number} could not be sent for ticket {ticket_id}!")
            return

        append_note_response = await self._append_reminder_note(ticket_id, service_number)
        if append_note_response["status"] not in range(200, 300):
            logger.error(f"Reminder note of edge {service_number} could not be appended to ticket {ticket_id}!")
            return

        logger.info(f"Reminder note of edge {service_number} was successfully appended to ticket {ticket_id}!")
        await self._notifications_repository.notify_successful_reminder_note_append(ticket_id, service_number)

    def _was_last_reminder_sent_recently(
        self, ticket_notes: list, ticket_creation_date: str, max_seconds_since_last_reminder: int
    ) -> bool:
        reminder_regex = REMINDER_NOTE_REGEX
        return self._utils_repository.has_last_event_happened_recently(
            ticket_notes,
            ticket_creation_date,
            max_seconds_since_last_event=max_seconds_since_last_reminder,
            regex=reminder_regex,
        )

    async def _append_reminder_note(self, ticket_id: int, service_number: str):
        reminder_note = self._ticket_repository.build_reminder_note()
        return await self._bruin_repository.append_note_to_ticket(
            ticket_id,
            reminder_note,
            service_numbers=[service_number],
        )
