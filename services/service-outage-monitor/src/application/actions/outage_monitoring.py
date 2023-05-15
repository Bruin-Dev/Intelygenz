import asyncio
import base64
import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from ipaddress import ip_address
from time import perf_counter
from typing import List, Optional, Pattern

from application import (
    DIGI_NOTE_REGEX,
    LINK_INFO_REGEX,
    OUTAGE_TYPE_REGEX,
    REMINDER_NOTE_REGEX,
    REOPEN_NOTE_REGEX,
    TRIAGE_NOTE_REGEX,
    ForwardQueues,
    Outages,
)
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from dateutil.parser import parse
from framework.storage.task_dispatcher_client import TaskTypes
from pytz import timezone, utc
from shortuuid import uuid

logger = logging.getLogger(__name__)


class OutageMonitor:
    def __init__(
        self,
        scheduler,
        task_dispatcher_client,
        config,
        utils_repository,
        outage_repository,
        bruin_repository,
        velocloud_repository,
        notifications_repository,
        triage_repository,
        customer_cache_repository,
        metrics_repository,
        digi_repository,
        ha_repository,
        email_repository,
    ):
        self._scheduler = scheduler
        self._task_dispatcher_client = task_dispatcher_client
        self._config = config
        self._utils_repository = utils_repository
        self._outage_repository = outage_repository
        self._bruin_repository = bruin_repository
        self._velocloud_repository = velocloud_repository
        self._notifications_repository = notifications_repository
        self._triage_repository = triage_repository
        self._customer_cache_repository = customer_cache_repository
        self._metrics_repository = metrics_repository
        self._digi_repository = digi_repository
        self._ha_repository = ha_repository
        self._email_repository = email_repository

        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG["semaphore"])

        self.__reset_state()

    def __reset_state(self):
        self._customer_cache = []
        self._autoresolve_serials_whitelist = set()
        self._velocloud_links_by_host = {}

    async def start_service_outage_monitoring(self, exec_on_start):
        logger.info("Scheduling Service Outage Monitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            logger.info("Service Outage Monitor job is going to be executed immediately")

        try:
            self._scheduler.add_job(
                self._outage_monitoring_process,
                "interval",
                seconds=self._config.MONITOR_CONFIG["jobs_intervals"]["outage_monitor"],
                next_run_time=next_run_time,
                replace_existing=False,
                id="_service_outage_monitor_process",
            )
        except ConflictingIdError as conflict:
            logger.error(f"Skipping start of Service Outage Monitoring job. Reason: {conflict}")

    async def _outage_monitoring_process(self):
        self.__reset_state()

        logger.info(f"Starting Service Outage Monitor process now...")
        start = time.time()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_outage_monitoring()
        if customer_cache_response["status"] not in range(200, 300) or customer_cache_response["status"] == 202:
            logger.error(
                f"Error while getting VeloCloud's customer cache: {customer_cache_response}. "
                f"Skipping Service Outage monitoring process..."
            )
            return

        cache = customer_cache_response["body"]
        logger.info(f"Got customer cache with {len(cache)} monitorable edges")

        logger.info("Ignoring blacklisted edges...")
        self._customer_cache = [
            elem
            for elem in customer_cache_response["body"]
            if elem["edge"] not in self._config.MONITOR_CONFIG["blacklisted_edges"]
        ]
        logger.info(f"Got {len(cache)} monitorable edges after filtering out blacklisted ones")

        serials_for_monitoring = [edge["serial_number"] for edge in self._customer_cache]
        logger.info(f"Monitorable serials: {serials_for_monitoring}")

        logger.info("Creating list of whitelisted serials for auto-resolve...")
        autoresolve_filter = self._config.MONITOR_CONFIG["velocloud_instances_filter"].keys()
        autoresolve_filter_enabled = len(autoresolve_filter) > 0
        if not autoresolve_filter_enabled:
            logger.info("Auto-resolve whitelist is not enabled, so all edges will be monitored")
            self._autoresolve_serials_whitelist = set(elem["serial_number"] for elem in self._customer_cache)
        else:
            self._autoresolve_serials_whitelist = set(
                elem["serial_number"] for elem in self._customer_cache if elem["edge"]["host"] in autoresolve_filter
            )
            logger.info(f"Got {len(self._autoresolve_serials_whitelist)} edges whitelisted for auto-resolves")

        split_cache = defaultdict(list)
        logger.info("Splitting cache by VeloCloud host")
        for edge_info in self._customer_cache:
            split_cache[edge_info["edge"]["host"]].append(edge_info)
        logger.info("Cache split")

        process_tasks = [self._process_velocloud_host(host, split_cache[host]) for host in split_cache]
        await asyncio.gather(*process_tasks, return_exceptions=True)

        stop = time.time()
        logger.info(
            f"[outage_monitoring_process] Outage monitoring process finished! Elapsed time:"
            f"{round((stop - start) / 60, 2)} minutes"
        )

    async def _process_velocloud_host(self, host, host_cache):
        logger.info(f"Processing {len(host_cache)} edges in Velocloud {host}...")
        start = perf_counter()

        links_with_edge_info_response = await self._velocloud_repository.get_links_with_edge_info(velocloud_host=host)
        if links_with_edge_info_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting links with edge info for VeloCloud host {host}: {links_with_edge_info_response}. "
                f"Skipping monitoring process for this host..."
            )
            return

        network_enterprises_response = await self._velocloud_repository.get_network_enterprises(velocloud_host=host)
        if network_enterprises_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting network enterprises for VeloCloud host {host}: {network_enterprises_response}. "
                f"Skipping monitoring process for this host..."
            )
            return

        links_with_edge_info: list = links_with_edge_info_response["body"]
        edges_network_enterprises: list = network_enterprises_response["body"]

        self._velocloud_links_by_host[host] = links_with_edge_info
        logger.info(f"Link status with edge info from Velocloud: {links_with_edge_info}")
        links_grouped_by_edge = self._velocloud_repository.group_links_by_edge(links_with_edge_info)

        logger.info(
            "Adding HA info to existing edges, and putting standby edges under monitoring as if they were "
            "standalone edges..."
        )
        edges_with_ha_info = self._ha_repository.map_edges_with_ha_info(
            links_grouped_by_edge, edges_network_enterprises
        )
        all_edges = self._ha_repository.get_edges_with_standbys_as_standalone_edges(edges_with_ha_info)

        serials_with_ha_disabled = [
            edge["edgeSerialNumber"] for edge in all_edges if not self._ha_repository.is_ha_enabled(edge)
        ]
        serials_with_ha_enabled = [
            edge["edgeSerialNumber"] for edge in all_edges if self._ha_repository.is_ha_enabled(edge)
        ]
        primary_serials = [edge["edgeSerialNumber"] for edge in all_edges if self._ha_repository.is_ha_primary(edge)]
        standby_serials = [edge["edgeSerialNumber"] for edge in all_edges if self._ha_repository.is_ha_standby(edge)]
        logger.info(f"Service Outage monitoring is about to check {len(all_edges)} edges for host {host}")
        logger.info(f"{len(serials_with_ha_disabled)} edges have HA disabled: {serials_with_ha_disabled}")
        logger.info(f"{len(serials_with_ha_enabled)} edges have HA enabled: {serials_with_ha_enabled}")
        logger.info(f"{len(primary_serials)} edges are the primary of a HA pair: {primary_serials}")
        logger.info(f"{len(standby_serials)} edges are the standby of a HA pair: {standby_serials}")

        logger.info(f"Mapping cached edges with their statuses...")
        edges_full_info = self._map_cached_edges_with_edges_status(host_cache, all_edges)
        mapped_serials_w_status = [edge["cached_info"]["serial_number"] for edge in edges_full_info]
        logger.info(f"Mapped cache serials with status: {mapped_serials_w_status}")

        for outage_type in Outages:
            down_edges = self._outage_repository.filter_edges_by_outage_type(edges_full_info, outage_type)
            logger.info(f'{outage_type.value} serials: {[e["status"]["edgeSerialNumber"] for e in down_edges]}')

            relevant_down_edges = [
                edge for edge in down_edges if self._outage_repository.should_document_outage(edge["status"])
            ]
            logger.info(
                f"{outage_type.value} serials that should be documented: "
                f'{[e["status"]["edgeSerialNumber"] for e in relevant_down_edges]}'
            )

            if relevant_down_edges:
                logger.info(f"{len(relevant_down_edges)} edges were detected in {outage_type.value} state.")
                edges_with_business_grade_links_down = [
                    edge
                    for edge in relevant_down_edges
                    if outage_type in [Outages.LINK_DOWN, Outages.HA_LINK_DOWN]
                    if edge["cached_info"]["edge"]["host"] == "metvco04.mettel.net"
                    if self._has_business_grade_link_down(edge["status"]["links"])
                ]

                logger.info(
                    f"[{outage_type.value}] {len(edges_with_business_grade_links_down)} out of "
                    f"{len(relevant_down_edges)} edges have at least one Business Grade link down. "
                    f"Skipping the quarantine, and attempting to create tickets for all of them..."
                )
                business_grade_tasks = [
                    self._attempt_ticket_creation(edge, outage_type) for edge in edges_with_business_grade_links_down
                ]
                out = await asyncio.gather(*business_grade_tasks, return_exceptions=True)
                for ex in filter(None, out):
                    logger.error(
                        f"[{outage_type.value}] Error while attempting ticket creation(s) for edge "
                        f"with Business Grade Link(s): {ex}"
                    )

                regular_edges = [
                    edge for edge in relevant_down_edges if edge not in edges_with_business_grade_links_down
                ]

                logger.info(
                    f"{len(regular_edges)} out of {len(relevant_down_edges)} have no Business Grade link(s) down. "
                    f"These edges will sit in the quarantine for some time before attempting to create tickets"
                )
                self._schedule_recheck_job_for_edges(regular_edges, outage_type)
            else:
                logger.info(
                    f"No edges were detected in {outage_type.value} state. "
                    f"No ticket creations will trigger for this outage type"
                )

        healthy_edges = [edge for edge in edges_full_info if self._outage_repository.is_edge_up(edge["status"])]
        logger.info(f'Healthy serials: {[e["status"]["edgeSerialNumber"] for e in healthy_edges]}')
        if healthy_edges:
            logger.info(
                f"{len(healthy_edges)} edges were detected in healthy state. Running autoresolve for all of them..."
            )
            autoresolve_tasks = [self._run_ticket_autoresolve_for_edge(edge) for edge in healthy_edges]
            await asyncio.gather(*autoresolve_tasks)
        else:
            logger.info("No edges were detected in healthy state. Autoresolve won't be triggered")

        stop = perf_counter()
        logger.info(f"Elapsed time processing edges in host {host}: {round((stop - start) / 60, 2)} minutes")

    def _schedule_recheck_job_for_edges(self, edges: list, outage_type: Outages):
        logger.info(f"Scheduling recheck job for {len(edges)} edges in {outage_type.value} state...")

        tz = timezone(self._config.TIMEZONE)
        current_datetime = datetime.now(tz)
        quarantine_time = self._config.MONITOR_CONFIG["quarantine"][outage_type]
        run_date = current_datetime + timedelta(seconds=quarantine_time)

        self._scheduler.add_job(
            self._recheck_edges_for_ticket_creation,
            "date",
            args=[edges, outage_type],
            run_date=run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f"{outage_type.value}_ticket_creation_recheck",
        )

        logger.info(f"Edges in {outage_type.value} state scheduled for recheck successfully")

    def _map_cached_edges_with_edges_status(self, customer_cache: list, edges_status: list) -> list:
        result = []

        cached_edges_by_serial = {elem["serial_number"]: elem for elem in customer_cache}
        edge_statuses_by_serial = {elem["edgeSerialNumber"]: elem for elem in edges_status}

        for serial_number, cached_edge in cached_edges_by_serial.items():
            edge_status = edge_statuses_by_serial.get(serial_number)
            if not edge_status:
                logger.warning(f'No edge status was found for cached edge {cached_edge["serial_number"]}. Skipping...')
                continue

            result.append(
                {
                    "cached_info": cached_edge,
                    "status": edge_status,
                }
            )

        return result

    async def _run_ticket_autoresolve_for_edge(self, edge: dict):
        async with self._semaphore:
            cached_edge = edge["cached_info"]
            serial_number = cached_edge["serial_number"]
            client_id = cached_edge["bruin_client_info"]["client_id"]
            client_name = cached_edge["bruin_client_info"]["client_name"]
            logical_ids = cached_edge["logical_ids"]
            links = edge["status"]["links"]

            logger.info(f"Starting autoresolve for edge {serial_number}...")

            if serial_number not in self._autoresolve_serials_whitelist:
                logger.info(f"Skipping autoresolve for edge {serial_number} because its serial is not whitelisted")
                return

            outage_ticket_response = await self._bruin_repository.get_open_outage_tickets(
                client_id=client_id, service_number=serial_number
            )
            outage_ticket_response_body = outage_ticket_response["body"]
            outage_ticket_response_status = outage_ticket_response["status"]
            if outage_ticket_response_status not in range(200, 300):
                logger.error(
                    f"Error while getting open Service Outage tickets for edge {serial_number}: "
                    f"{outage_ticket_response}. Skipping autoresolve..."
                )
                return

            if not outage_ticket_response_body:
                logger.info(f"No open Service Outage ticket found for edge {serial_number}. Skipping autoresolve...")
                return

            outage_ticket: dict = outage_ticket_response_body[0]
            outage_ticket_id = outage_ticket["ticketID"]
            outage_ticket_creation_date = outage_ticket["createDate"]
            outage_ticket_severity = outage_ticket["severity"]

            if not self._was_ticket_created_by_automation_engine(outage_ticket):
                logger.info(
                    f"Ticket {outage_ticket_id} for edge {serial_number} was not created by Automation Engine. "
                    f"Skipping autoresolve..."
                )
                return

            ticket_details_response = await self._bruin_repository.get_ticket_details(outage_ticket_id)
            ticket_details_response_body = ticket_details_response["body"]
            ticket_details_response_status = ticket_details_response["status"]
            if ticket_details_response_status not in range(200, 300):
                logger.error(
                    f"Error while getting details of ticket {outage_ticket_id}: {ticket_details_response}. "
                    f"Skipping autoresolve..."
                )
                return

            details_from_ticket = ticket_details_response_body["ticketDetails"]
            detail_for_ticket_resolution = self._utils_repository.get_first_element_matching(
                details_from_ticket,
                lambda detail: detail["detailValue"] == serial_number,
            )
            ticket_detail_id = detail_for_ticket_resolution["detailID"]

            notes_from_outage_ticket = ticket_details_response_body["ticketNotes"]

            healthy_link_interfaces = [
                link["interface"]
                for link in links
            ]

            detailIds_service_numbers_and_interfaces = (
                await self._get_resolved_detailIds_service_numbers_and_interfaces(
                    outage_ticket_id, ticket_detail_id, healthy_link_interfaces, details_from_ticket)
            )

            resolved_faulty_interfaces = [
                detailId_service_number_and_interface["interface"]
                for detailId_service_number_and_interface in detailIds_service_numbers_and_interfaces
            ]

            logger.info(f"Resolved faulty interfaces for ticket {outage_ticket_id}: {resolved_faulty_interfaces}.")

            service_numbers = [serial_number]

            for detailId_service_number_and_interface in detailIds_service_numbers_and_interfaces:
                service_numbers.append(detailId_service_number_and_interface["service_number"])

            logger.info(f"Resolved Service numbers for ticket {outage_ticket_id}: {service_numbers}.")

            relevant_notes = [
                note
                for note in notes_from_outage_ticket
                if note["serviceNumber"] is not None
                if any(service_number in service_numbers for service_number in note["serviceNumber"])
                if note["noteValue"] is not None
            ]

            last_cycle_notes = self._get_notes_appended_since_latest_reopen_or_ticket_creation(relevant_notes)
            triage_note = self._get_triage_or_reopen_note(last_cycle_notes)
            outage_type = self._get_outage_type_from_ticket_notes(last_cycle_notes)
            has_faulty_digi_link = self._get_has_faulty_digi_link_from_ticket_notes(last_cycle_notes, triage_note)
            has_faulty_byob_link = self._get_has_faulty_byob_link_from_triage_note(triage_note)
            faulty_link_types = self._get_faulty_link_types_from_triage_note(triage_note)
            is_task_in_ipa_queue = self._is_ticket_task_in_ipa_queue(detail_for_ticket_resolution)

            link_access_types = self._get_link_access_types_from_affecting_trouble_note(
                resolved_faulty_interfaces, logical_ids)
            is_task_assigned = self._is_ticket_task_assigned(detail_for_ticket_resolution)

            if has_faulty_byob_link and is_task_in_ipa_queue:
                logger.info(
                    f"Task for serial {serial_number} in ticket {outage_ticket_id} is related to a BYOB link "
                    f"and is in the IPA Investigate queue. Ignoring auto-resolution restrictions..."
                )

            elif self._is_ethernet_link_access_type(link_access_types) and is_task_assigned:
                logger.info(
                    f"Task for serial {serial_number} in ticket {outage_ticket_id} is related to an Ethernet link"
                    f" and is assigned. Ignoring auto-resolution..."
                )
                return

            else:
                max_seconds_since_last_outage = self._get_max_seconds_since_last_outage(edge)
                was_last_outage_detected_recently = self._has_last_event_happened_recently(
                    ticket_notes=relevant_notes,
                    documentation_cycle_start_date=outage_ticket_creation_date,
                    max_seconds_since_last_event=max_seconds_since_last_outage,
                    note_regex=REOPEN_NOTE_REGEX,
                )
                if not was_last_outage_detected_recently:
                    logger.info(
                        f"Edge {serial_number} has been in outage state for a long time, so the task from ticket "
                        f"{outage_ticket_id} will not be autoresolved. Skipping autoresolve..."
                    )
                    return

                can_detail_be_autoresolved_one_more_time = (
                    self._outage_repository.is_outage_ticket_detail_auto_resolvable(
                        notes_from_outage_ticket,
                        serial_number,
                        max_autoresolves=self._config.MONITOR_CONFIG["autoresolve"]["max_autoresolves"],
                    )
                )
                if not can_detail_be_autoresolved_one_more_time:
                    logger.info(
                        f"Limit to autoresolve task of ticket {outage_ticket_id} for edge {serial_number} "
                        f"has been maxed out already. Skipping autoresolve..."
                    )
                    return

            if self._is_detail_resolved(detail_for_ticket_resolution):
                logger.info(
                    f"Task of ticket {outage_ticket_id} for edge {serial_number} is already resolved. "
                    f"Skipping autoresolve..."
                )
                return

            working_environment = self._config.CURRENT_ENVIRONMENT
            if working_environment != "production":
                logger.info(
                    f"[ticket-autoresolve] Skipping autoresolve for edge {serial_number} since the "
                    f"current environment is {working_environment.upper()}."
                )
                return

            logger.info(f"Autoresolving task of ticket {outage_ticket_id} for edge {serial_number}...")
            await self._bruin_repository.unpause_ticket_detail(
                outage_ticket_id, service_number=serial_number, detail_id=ticket_detail_id
            )
            resolve_ticket_response = await self._bruin_repository.resolve_ticket(
                outage_ticket_id, ticket_detail_id, resolved_faulty_interfaces)
            if resolve_ticket_response["status"] not in range(200, 300):
                logger.error(
                    f"Error while resolving task of ticket {outage_ticket_id} for edge {serial_number}: "
                    f"{resolve_ticket_response}. Skipping autoresolve ..."
                )
                return

            await self._bruin_repository.append_autoresolve_note_to_ticket(outage_ticket_id, serial_number)
            for detailId_service_number_and_interface in detailIds_service_numbers_and_interfaces:
                await self._bruin_repository.append_autoresolve_line_note_to_ticket(
                    outage_ticket_id, detailId_service_number_and_interface["service_number"])

            if has_faulty_byob_link and is_task_in_ipa_queue:
                logger.info(f'Closing ticket {outage_ticket_id} for edge {serial_number} due to byob...')
                close_note = 'Closing ticket due to byob link.'
                close_ticket_response = await self._bruin_repository.close_ticket(outage_ticket_id, close_note)
                if close_ticket_response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while closing ticket {outage_ticket_id} for edge {serial_number}: "
                        f"{close_ticket_response}"
                    )

            await self._notify_successful_autoresolve(outage_ticket_id)

            self._metrics_repository.increment_tasks_autoresolved(
                client=client_name,
                outage_type=outage_type,
                severity=outage_ticket_severity,
                has_digi=has_faulty_digi_link,
                has_byob=has_faulty_byob_link,
                link_types=faulty_link_types,
            )
            logger.info(f"Task of ticket {outage_ticket_id} for edge {serial_number} was autoresolved!")

            task_type = TaskTypes.TICKET_FORWARDS
            task_key = f"{outage_ticket_id}-{serial_number}-{ForwardQueues.HNOC.name}"

            if self._task_dispatcher_client.clear_task(task_type, task_key):
                logger.info(
                    f"Removed scheduled task to forward to {ForwardQueues.HNOC.value} "
                    f"for auto-resolved task of ticket {outage_ticket_id} for edge {serial_number}"
                )

    def _was_ticket_created_by_automation_engine(self, ticket: dict) -> bool:
        return ticket["createdBy"] == self._config.IPA_SYSTEM_USERNAME_IN_BRUIN

    @staticmethod
    def _is_detail_resolved(ticket_detail: dict):
        return ticket_detail["detailStatus"] == "R"

    def _find_note(self, ticket_notes, watermark):
        return self._utils_repository.get_first_element_matching(
            iterable=ticket_notes, condition=lambda note: watermark in note.get("noteValue"), fallback=None
        )

    async def _notify_successful_autoresolve(self, ticket_id):
        message = f"Outage ticket {ticket_id} was autoresolved. Details at https://app.bruin.com/t/{ticket_id}"
        await self._notifications_repository.send_slack_message(message)

    async def _recheck_edges_for_ticket_creation(self, outage_edges: list, outage_type: Outages):
        logger.info(
            f"[{outage_type.value}] Re-checking {len(outage_edges)} edges in outage state prior to ticket creation..."
        )
        logger.info(f"[{outage_type.value}] Edges in outage before quarantine recheck: {outage_edges}")

        host = self._config.VELOCLOUD_HOST

        links_with_edge_info_response = await self._velocloud_repository.get_links_with_edge_info(velocloud_host=host)
        if links_with_edge_info_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting links with edge info for VeloCloud host {host}: {links_with_edge_info_response}. "
                f"Skipping recheck process for this host..."
            )
            return

        network_enterprises_response = await self._velocloud_repository.get_network_enterprises(velocloud_host=host)
        if network_enterprises_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting network enterprises for VeloCloud host {host}: {network_enterprises_response}. "
                f"Skipping recheck process for this host..."
            )
            return

        logger.info(
            f"[{outage_type.value}] Velocloud edge status response in quarantine recheck: "
            f"{links_with_edge_info_response}"
        )
        links_with_edge_info: list = links_with_edge_info_response["body"]
        edges_network_enterprises: list = network_enterprises_response["body"]

        links_grouped_by_edge = self._velocloud_repository.group_links_by_edge(links_with_edge_info)

        logger.info(
            f"[{outage_type.value}] Adding HA info to existing edges, and putting standby edges under monitoring as if "
            "they were standalone edges..."
        )
        edges_with_ha_info = self._ha_repository.map_edges_with_ha_info(
            links_grouped_by_edge, edges_network_enterprises
        )
        all_edges = self._ha_repository.get_edges_with_standbys_as_standalone_edges(edges_with_ha_info)

        customer_cache_for_outage_edges = [elem["cached_info"] for elem in outage_edges]
        edges_full_info = self._map_cached_edges_with_edges_status(customer_cache_for_outage_edges, all_edges)
        logger.info(f"[{outage_type.value}] Current status of edges that were in outage state: {edges_full_info}")

        edges_still_down = self._outage_repository.filter_edges_by_outage_type(edges_full_info, outage_type)
        serials_still_down = [edge["status"]["edgeSerialNumber"] for edge in edges_still_down]
        logger.info(f"[{outage_type.value}] Edges still in outage state after recheck: {edges_still_down}")
        logger.info(f"[{outage_type.value}] Serials still in outage state after recheck: {serials_still_down}")

        healthy_edges = [edge for edge in edges_full_info if self._outage_repository.is_edge_up(edge["status"])]
        healthy_serials = [edge["status"]["edgeSerialNumber"] for edge in healthy_edges]
        logger.info(f"[{outage_type.value}] Edges that are healthy after recheck: {healthy_edges}")
        logger.info(f"[{outage_type.value}] Serials that are healthy after recheck: {healthy_serials}")

        if edges_still_down:
            logger.info(
                f"[{outage_type.value}] {len(edges_still_down)} edges are still in outage state after re-check. "
                "Attempting outage ticket creation for all of them..."
            )

            working_environment = self._config.CURRENT_ENVIRONMENT
            if working_environment == "production":
                tasks = [self._attempt_ticket_creation(edge, outage_type) for edge in edges_still_down]
                out = await asyncio.gather(*tasks, return_exceptions=True)
                for ex in filter(None, out):
                    logger.error(
                        f"[{outage_type.value}] Error while attempting ticket creation(s) for edge in "
                        f"the quarantine: {ex}"
                    )
            else:
                logger.info(
                    f"[{outage_type.value}] Not starting outage ticket creation for {len(edges_still_down)} faulty "
                    f"edges because the current working environment is {working_environment.upper()}."
                )
        else:
            logger.info(
                f"[{outage_type.value}] No edges were detected in outage state after re-check. "
                "Outage tickets won't be created"
            )

        if healthy_edges:
            logger.info(
                f"[{outage_type.value}] {len(healthy_edges)} edges were detected in healthy state after re-check. '"
                "Running autoresolve for all of them..."
            )
            logger.info(f"[{outage_type.value}] Edges that are going to be attempted to autoresolve: {healthy_edges}")
            autoresolve_tasks = [self._run_ticket_autoresolve_for_edge(edge) for edge in healthy_edges]
            await asyncio.gather(*autoresolve_tasks)
        else:
            logger.info(
                f"[{outage_type.value}] No edges were detected in healthy state. Autoresolve won't be triggered"
            )

        logger.info(f"[{outage_type.value}] Re-check process finished for {len(outage_edges)} edges")

    def _get_hnoc_forward_time_by_outage_type(self, outage_type: Outages, edge: dict) -> float:
        if outage_type in [Outages.LINK_DOWN, Outages.HA_LINK_DOWN]:
            if edge["cached_info"]["edge"]["host"] == "metvco04.mettel.net" and self._has_business_grade_link_down(
                edge["status"]["links"]
            ):
                return self._config.MONITOR_CONFIG["jobs_intervals"]["forward_to_hnoc_business_grade"]
            else:
                max_seconds_since_last_outage = self._get_max_seconds_since_last_outage(edge)
                return max_seconds_since_last_outage / 60
        else:
            return self._config.MONITOR_CONFIG["jobs_intervals"]["forward_to_hnoc_edge_down"]

    def _should_forward_to_hnoc(self, link_data: list, is_edge_down: bool) -> bool:
        if is_edge_down:
            return True
        return self._has_faulty_non_blacklisted_link(link_data)

    def _schedule_forward_to_hnoc_queue(
        self,
        forward_time,
        ticket_id,
        serial_number,
        client_name,
        outage_type,
        severity,
        has_faulty_digi_link,
        has_faulty_byob_link,
        faulty_link_types,
    ):
        target_queue = ForwardQueues.HNOC
        current_datetime = datetime.utcnow()
        forward_task_run_date = current_datetime + timedelta(minutes=forward_time)

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
                    "outage_type": outage_type.value,
                    "severity": severity,
                    "target_queue": target_queue.value,
                    "has_digi": has_faulty_digi_link,
                    "has_byob": has_faulty_byob_link,
                    "link_types": faulty_link_types,
                },
            },
        )

    async def _append_triage_note(
        self, ticket_id: int, cached_edge: dict, edge_status: dict, outage_type: Outages, *, is_reopen_note=False
    ):
        edge_full_id = cached_edge["edge"]
        serial_number = cached_edge["serial_number"]

        logger.info(f"Appending Triage note to ticket {ticket_id} for edge {serial_number}...")

        past_moment_for_events_lookup = datetime.now(utc) - timedelta(days=7)

        recent_events_response = await self._velocloud_repository.get_last_edge_events(
            edge_full_id, since=past_moment_for_events_lookup
        )

        if recent_events_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting last events for edge {serial_number}: {recent_events_response}. "
                f"Skipping append Triage note..."
            )
            return

        recent_events = recent_events_response["body"]
        recent_events.sort(key=lambda event: event["eventTime"], reverse=True)

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        if ticket_details_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
                f"Skipping append Triage note..."
            )
            return

        ticket_detail: dict = ticket_details_response["body"]["ticketDetails"][0]
        ticket_note = self._triage_repository.build_triage_note(
            cached_edge, edge_status, recent_events, outage_type, is_reopen_note=is_reopen_note
        )

        detail_object = {
            "ticket_id": ticket_id,
            "ticket_detail": ticket_detail,
        }
        await self._bruin_repository.append_triage_note(detail_object, ticket_note)

        logger.info(f"Triage note appended to ticket {ticket_id} for edge {serial_number}")

    async def _reopen_outage_ticket(self, ticket_id: int, edge_status: dict, cached_edge: dict, outage_type: Outages):
        serial_number = edge_status["edgeSerialNumber"]
        logger.info(f"Reopening task for serial {serial_number} from ticket {ticket_id}...")

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response["body"]
        ticket_details_response_status = ticket_details_response["status"]
        if ticket_details_response_status not in range(200, 300):
            logger.error(
                f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
                f"Skipping re-opening ticket task..."
            )
            return

        ticket_detail_for_reopen = self._utils_repository.get_first_element_matching(
            ticket_details_response_body["ticketDetails"],
            lambda detail: detail["detailValue"] == serial_number,
        )
        detail_id_for_reopening = ticket_detail_for_reopen["detailID"]

        ticket_reopening_response = await self._bruin_repository.open_ticket(ticket_id, detail_id_for_reopening)
        ticket_reopening_response_status = ticket_reopening_response["status"]

        if ticket_reopening_response_status == 200:
            logger.info(f"Task for edge {serial_number} of ticket {ticket_id} re-opened!")
            slack_message = (
                f"Task for edge {serial_number} of ticket {ticket_id} reopened: https://app.bruin.com/t/{ticket_id}"
            )
            await self._notifications_repository.send_slack_message(slack_message)
            await self._append_triage_note(ticket_id, cached_edge, edge_status, outage_type, is_reopen_note=True)
            return True
        else:
            logger.error(
                f"Error while re-opening task for edge {serial_number} of ticket {ticket_id}: "
                f"{ticket_reopening_response}"
            )
            return False

    async def _check_for_digi_reboot(self, ticket_id, logical_id_list, serial_number, edge_status):
        logger.info(f"Checking edge {serial_number} for DiGi Links")
        digi_links = self._digi_repository.get_digi_links(logical_id_list)

        for digi_link in digi_links:
            link_status = next(
                (link for link in edge_status["links"] if link["interface"] == digi_link["interface_name"]), None
            )
            if link_status is not None and self._outage_repository.is_faulty_link(link_status["linkState"]):
                logger.info(f"Rebooting DiGi link {digi_link['interface_name']} from edge {serial_number}...")
                reboot = await self._digi_repository.reboot_link(serial_number, ticket_id, digi_link["logical_id"])

                if reboot["status"] not in range(200, 300):
                    logger.error(
                        f"Error while rebooting DiGi link {digi_link['interface_name']} from edge {serial_number}: "
                        f"{reboot}. Skipping reboot for this link..."
                    )
                    continue

                logger.info(f"DiGi link {digi_link['interface_name']} from edge {serial_number} rebooted!")

                slack_message = (
                    f"DiGi reboot started for faulty edge {serial_number}. Ticket "
                    f"details at https://app.bruin.com/t/{ticket_id}."
                )
                await self._notifications_repository.send_slack_message(slack_message)

                logger.info(
                    f"Appending Reboot note for DiGi link {digi_link['interface_name']} from edge {serial_number} "
                    f"to ticket {ticket_id}..."
                )
                append_digi_reboot_note_response = await self._bruin_repository.append_digi_reboot_note(
                    ticket_id, serial_number, digi_link["interface_name"]
                )
                if append_digi_reboot_note_response not in range(200, 300):
                    logger.error(
                        f"Error while appending Reboot note to ticket {ticket_id} for DiGi link "
                        f"{digi_link['interface_name']} from edge {serial_number}: {append_digi_reboot_note_response}"
                    )
                    continue

                logger.info(
                    f"Reboot note for DiGi link {digi_link['interface_name']} from edge {serial_number} "
                    f"appended to ticket {ticket_id}!"
                )
            else:
                logger.info(
                    f"DiGi link {digi_link['interface_name']} from edge {serial_number} is not down. "
                    f"Skipping reboot for this link..."
                )

    async def _check_for_failed_digi_reboot(
        self,
        ticket_id,
        logical_id_list,
        serial_number,
        edge_status,
        client_name,
        outage_type,
        severity,
        has_faulty_digi_link,
        has_faulty_byob_link,
        faulty_link_types,
    ):
        if self._outage_repository.is_faulty_edge(edge_status["edgeState"]):
            logger.info(
                f"Edge {serial_number} is not under a Link Down outage at this moment. "
                f"Skipping checking for failed DiGi reboots..."
            )
            return

        logger.info(f"Checking edge {serial_number} for DiGi Links")
        digi_links = self._digi_repository.get_digi_links(logical_id_list)

        for digi_link in digi_links:
            link_status = next(
                (link for link in edge_status["links"] if link["interface"] == digi_link["interface_name"]), None
            )
            if link_status is not None and self._outage_repository.is_faulty_link(link_status["linkState"]):
                logger.info(f"Checking for failed reboots for edge {serial_number}...")

                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                ticket_details_response_body = ticket_details_response["body"]
                ticket_details_response_status = ticket_details_response["status"]
                if ticket_details_response_status not in range(200, 300):
                    logger.error(
                        f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
                        f"Skipping checking for failed DiGi reboots for this edge..."
                    )
                    return

                details_from_ticket = ticket_details_response_body["ticketDetails"]
                detail_for_ticket_resolution = self._utils_repository.get_first_element_matching(
                    details_from_ticket,
                    lambda detail: detail["detailValue"] == serial_number,
                )
                ticket_detail_id = detail_for_ticket_resolution["detailID"]

                notes_from_outage_ticket = ticket_details_response_body["ticketNotes"]
                logger.info(f"Notes of ticket {ticket_id} for edge {serial_number}: {notes_from_outage_ticket}")

                relevant_notes = [
                    note
                    for note in notes_from_outage_ticket
                    if note["serviceNumber"] is not None
                    if serial_number in note["serviceNumber"]
                    if note["noteValue"] is not None
                ]
                digi_note = self._find_note(relevant_notes, "DiGi")

                if digi_note is None:
                    logger.info(
                        f"No DiGi note was found for ticket {ticket_id} and edge {serial_number}. "
                        f"Skipping checking for failed DiGi reboots for this edge..."
                    )
                    return

                if self._was_digi_rebooted_recently(digi_note):
                    logger.info(
                        f"The last DiGi reboot attempt for edge {serial_number} occurred "
                        f'{self._config.MONITOR_CONFIG["last_digi_reboot_seconds"] / 60} or less minutes ago. '
                        f"Skipping checking for failed DiGi reboots for this edge..."
                    )
                    return

                digi_note_interface_name = self._digi_repository.get_interface_name_from_digi_note(digi_note)

                if digi_note_interface_name == link_status["interface"]:
                    logger.info(
                        f"Found DiGi Reboot note in ticket {ticket_id} for link {link_status['interface']} "
                        f"from edge {serial_number}. "
                        f"Since the link is still down, it's fair to assume the last DiGi reboot failed. "
                        f"Checking to see if the ticket task for this edge should be forwarded to the Wireless team..."
                    )

                    target_queue = ForwardQueues.WIRELESS.value
                    task_result_note = self._find_note(relevant_notes, target_queue)

                    if task_result_note is not None:
                        logger.info(
                            f"Task for edge {serial_number} from ticket {ticket_id} has already been forwarded "
                            f"to {target_queue}. Skipping forward..."
                        )
                        return

                    logger.info(
                        f"Forwarding ticket task of {ticket_id} for edge {serial_number} to the Wireless team..."
                    )
                    change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
                        ticket_id, target_queue, serial_number=serial_number, detail_id=ticket_detail_id
                    )
                    if change_detail_work_queue_response["status"] not in range(200, 300):
                        logger.error(
                            f"Error while forwarding ticket task of {ticket_id} for edge {serial_number} to "
                            f"the Wireless team: {change_detail_work_queue_response}."
                        )
                        return

                    logger.info(f"Ticket task of {ticket_id} for edge {serial_number} forwarded to the Wireless team!")

                    self._metrics_repository.increment_tasks_forwarded(
                        client=client_name,
                        outage_type=outage_type.value,
                        severity=severity,
                        target_queue=target_queue,
                        has_digi=has_faulty_digi_link,
                        has_byob=has_faulty_byob_link,
                        link_types=faulty_link_types,
                    )
                    await self._bruin_repository.append_task_result_change_note(ticket_id, target_queue)
                    slack_message = f"Forwarding ticket {ticket_id} to Wireless team"
                    await self._notifications_repository.send_slack_message(slack_message)
                else:
                    logger.info(
                        f"Found a DiGi Reboot note in ticket {ticket_id}, but it is not related to link "
                        f"{link_status['interface']} from edge {serial_number}. "
                        f"Attempting DiGi reboot for this link..."
                    )

                    reboot = await self._digi_repository.reboot_link(serial_number, ticket_id, digi_link["logical_id"])
                    if reboot["status"] not in range(200, 300):
                        logger.error(
                            f"Error while rebooting DiGi link {digi_link['interface_name']} from edge {serial_number}: "
                            f"{reboot}. Skipping reboot for this link..."
                        )
                        return

                    logger.info(f"DiGi link {digi_link['interface_name']} from edge {serial_number} rebooted!")

                    logger.info(
                        f"Appending Reboot note for DiGi link {digi_link['interface_name']} from edge {serial_number} "
                        f"to ticket {ticket_id}..."
                    )
                    await self._bruin_repository.append_digi_reboot_note(
                        ticket_id, serial_number, digi_link["interface_name"]
                    )
                    slack_message = (
                        f"DiGi reboot started for faulty edge {serial_number}. Ticket "
                        f"details at https://app.bruin.com/t/{ticket_id}."
                    )
                    await self._notifications_repository.send_slack_message(slack_message)
            else:
                logger.info(
                    f"DiGi link {digi_link['interface_name']} from edge {serial_number} is not down. "
                    f"Skipping checking for failed DiGi reboot for this link..."
                )

    async def _attempt_forward_to_asr(
        self,
        cached_edge,
        edge_status,
        ticket_id,
        client_name,
        outage_type,
        severity,
        has_faulty_digi_link,
        has_faulty_byob_link,
        faulty_link_types,
    ):
        serial_number = cached_edge["serial_number"]
        logger.info(
            f"Attempting to forward task of ticket {ticket_id} related to serial {serial_number} to ASR Investigate..."
        )

        links_configuration = cached_edge["links_configuration"]
        if self._outage_repository.is_faulty_edge(edge_status["edgeState"]):
            logger.info(
                f"Outage of edge {serial_number} is caused by a faulty edge. Related task of ticket {ticket_id} "
                "will not be forwarded to ASR Investigate."
            )
            return

        logger.info(f"Searching for any disconnected wired links in edge {serial_number}...")
        links_wired = self._outage_repository.find_disconnected_wired_links(edge_status, links_configuration)
        if not links_wired:
            logger.info(
                f"No wired links are disconnected for edge {serial_number}. Related task of ticket {ticket_id} "
                "will not be forwarded to ASR Investigate."
            )
            return

        logger.info(
            f"Filtering out any of the wired links of edge {serial_number} that contains any of the "
            f'following: {self._config.MONITOR_CONFIG["blacklisted_link_labels_for_asr_forwards"]} '
            f"in the link label"
        )
        whitelisted_links = self._find_whitelisted_links_for_asr_forward(links_wired)
        if not whitelisted_links:
            logger.info(
                f"No links with whitelisted labels were found for edge {serial_number}. "
                f"Related task of ticket {ticket_id} will not be forwarded to ASR Investigate."
            )
            return

        ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
        ticket_details_response_body = ticket_details_response["body"]
        ticket_details_response_status = ticket_details_response["status"]
        if ticket_details_response_status not in range(200, 300):
            logger.error(f"Error while getting details of ticket {ticket_id}. Skipping forward to ASR...")
            return

        details_from_ticket = ticket_details_response_body["ticketDetails"]
        detail_for_ticket_resolution = self._utils_repository.get_first_element_matching(
            details_from_ticket,
            lambda detail: detail["detailValue"] == serial_number,
        )
        ticket_detail_id = detail_for_ticket_resolution["detailID"]

        notes_from_outage_ticket = ticket_details_response_body["ticketNotes"]
        logger.info(f"Notes of ticket {ticket_id} for edge {serial_number}: {notes_from_outage_ticket}")

        relevant_notes = [
            note
            for note in notes_from_outage_ticket
            if note["serviceNumber"] is not None
            if serial_number in note["serviceNumber"]
            if note["noteValue"] is not None
        ]

        target_queue = ForwardQueues.ASR.value
        task_result = "No Trouble Found - Carrier Issue"
        task_result_note = self._find_note(relevant_notes, target_queue)

        if task_result_note is not None:
            logger.info(
                f"Task related to edge {serial_number} of ticket {ticket_id} has already been forwarded to "
                f'"{target_queue}"'
            )
            return

        logger.info(f"Forwarding task from ticket {ticket_id} related to edge {serial_number} to ASR...")
        change_detail_work_queue_response = await self._bruin_repository.change_detail_work_queue(
            ticket_id, task_result, serial_number=serial_number, detail_id=ticket_detail_id
        )
        if change_detail_work_queue_response["status"] not in range(200, 300):
            logger.error(
                f"Error while forwarding ticket task of {ticket_id} for edge {serial_number} to "
                f"ASR: {change_detail_work_queue_response}."
            )
            return

        logger.info(f"Ticket task of {ticket_id} for edge {serial_number} forwarded to ASR!")

        self._metrics_repository.increment_tasks_forwarded(
            client=client_name,
            outage_type=outage_type.value,
            severity=severity,
            target_queue=target_queue,
            has_digi=has_faulty_digi_link,
            has_byob=has_faulty_byob_link,
            link_types=faulty_link_types,
        )
        await self._bruin_repository.append_asr_forwarding_note(ticket_id, whitelisted_links, serial_number)
        slack_message = (
            f"Task of ticket {ticket_id} related to serial {serial_number} was successfully forwarded "
            f"to {target_queue} queue!"
        )
        await self._notifications_repository.send_slack_message(slack_message)

    @staticmethod
    def _is_link_label_an_ip(link_label: str):
        try:
            return bool(ip_address(link_label))
        except ValueError:
            return False

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

    def _find_whitelisted_links_for_asr_forward(self, links: list) -> list:
        return [
            link
            for link in links
            if not self._is_link_label_blacklisted_from_asr(link["displayName"])
            if not self._is_link_label_an_ip(link["displayName"])
        ]

    def _has_faulty_digi_link(self, links: List[dict], logical_id_list: List[dict]) -> bool:
        digi_links = self._digi_repository.get_digi_links(logical_id_list)
        digi_interfaces = [link["interface_name"] for link in digi_links]

        return any(
            link
            for link in links
            if link["interface"] in digi_interfaces
            if self._outage_repository.is_faulty_link(link["linkState"])
        )

    def _has_faulty_blacklisted_link(self, links: List[dict]) -> bool:
        return any(
            link
            for link in links
            if self._is_link_label_blacklisted_from_hnoc(link["displayName"])
            if self._outage_repository.is_faulty_link(link["linkState"])
        )

    def _has_faulty_non_blacklisted_link(self, links: List[dict]) -> bool:
        return any(
            link
            for link in links
            if not self._is_link_label_blacklisted_from_hnoc(link["displayName"])
            if self._outage_repository.is_faulty_link(link["linkState"])
        )

    def _get_faulty_link_types(self, links: List[dict], links_configuration: List[dict]) -> List[str]:
        return list(
            {
                self._outage_repository.get_link_type(link, links_configuration)
                for link in links
                if self._outage_repository.is_faulty_link(link["linkState"])
            }
        )

    def _get_faulty_link_interfaces(self, links: List[dict]) -> List[str]:
        return list(
            {
                link['interface']
                for link in links
                if self._outage_repository.is_faulty_link(link["linkState"])
            }
        )

    def _was_digi_rebooted_recently(self, ticket_note) -> bool:
        current_datetime = datetime.now(utc)
        max_seconds_since_last_outage = self._config.MONITOR_CONFIG["last_digi_reboot_seconds"]

        note_creation_date = parse(ticket_note["createdDate"]).astimezone(utc)
        seconds_elapsed_since_last_outage = (current_datetime - note_creation_date).total_seconds()
        return seconds_elapsed_since_last_outage < max_seconds_since_last_outage

    def _is_ticket_old_enough(self, ticket_creation_date: str) -> bool:
        current_datetime = datetime.now().astimezone(utc)
        max_seconds_since_creation = self._config.MONITOR_CONFIG["forward_link_outage_seconds"]

        ticket_creation_datetime = parse(ticket_creation_date).replace(tzinfo=utc)
        seconds_elapsed_since_creation = (current_datetime - ticket_creation_datetime).total_seconds()

        return seconds_elapsed_since_creation >= max_seconds_since_creation

    def _get_target_severity(self, is_edge_down: bool):
        if is_edge_down:
            return self._config.MONITOR_CONFIG["severity_by_outage_type"]["edge_down"]
        else:
            return self._config.MONITOR_CONFIG["severity_by_outage_type"]["link_down"]

    async def _change_ticket_severity(
        self, ticket_id: int, edge_status: dict, target_severity: int, *, check_ticket_tasks: bool
    ):
        logger.info(f"Attempting to change severity level of ticket {ticket_id}...")

        serial_number = edge_status["edgeSerialNumber"]

        if self._outage_repository.is_faulty_edge(edge_status["edgeState"]):
            logger.info(
                f"Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue "
                f"is that edge {serial_number} is offline."
            )
            change_severity_task = self._bruin_repository.change_ticket_severity_for_offline_edge(ticket_id)
        else:
            if check_ticket_tasks:
                ticket_details_response = await self._bruin_repository.get_ticket_details(ticket_id)
                if ticket_details_response["status"] not in range(200, 300):
                    logger.error(
                        f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
                        f"Skipping ticket severity change..."
                    )
                    return

                ticket_tasks = ticket_details_response["body"]["ticketDetails"]
                if self._has_ticket_multiple_unresolved_tasks(ticket_tasks):
                    logger.info(
                        f"Severity level of ticket {ticket_id} will remain the same, as the root cause of the outage "
                        f"issue is that at least one link of edge {serial_number} is disconnected, and this ticket "
                        f"has multiple unresolved tasks."
                    )
                    return

            logger.info(
                f"Severity level of ticket {ticket_id} is about to be changed, as the root cause of the outage issue "
                f"is that at least one link of edge {serial_number} is disconnected, and this ticket has a single "
                "unresolved task."
            )
            disconnected_links = self._outage_repository.find_disconnected_links(edge_status["links"])
            disconnected_interfaces = [link["interface"] for link in disconnected_links]

            change_severity_task = self._bruin_repository.change_ticket_severity_for_disconnected_links(
                ticket_id, disconnected_interfaces
            )

        get_ticket_response = await self._bruin_repository.get_ticket(ticket_id)
        if not get_ticket_response["status"] in range(200, 300):
            logger.error(
                f"Error while getting overview of ticket {ticket_id}: {get_ticket_response}. "
                f"Skipping ticket severity change..."
            )
            change_severity_task.close()
            return

        ticket_info = get_ticket_response["body"]
        if self._is_ticket_already_in_severity_level(ticket_info, target_severity):
            logger.info(
                f"Ticket {ticket_id} is already in severity level {target_severity}, so there is no need "
                "to change it."
            )
            change_severity_task.close()
            return

        result = await change_severity_task
        if result["status"] not in range(200, 300):
            logger.error(
                f"Error while changing severity of ticket {ticket_id}: {result}. Skipping ticket severity change..."
            )
            return

        logger.info(f"Finished changing severity level of ticket {ticket_id} to {target_severity}!")

    def _has_ticket_multiple_unresolved_tasks(self, ticket_tasks: list) -> bool:
        unresolved_tasks = [task for task in ticket_tasks if not self._is_detail_resolved(task)]
        return len(unresolved_tasks) > 1

    @staticmethod
    def _is_ticket_already_in_severity_level(ticket_info: dict, severity_level: int) -> bool:
        return ticket_info["severity"] == severity_level

    @staticmethod
    def _is_ticket_task_in_ipa_queue(ticket_task: dict) -> bool:
        return ticket_task["currentTaskName"] == "IPA Investigate"

    @staticmethod
    def _is_ticket_task_assigned(ticket_task: dict) -> bool:
        assigned_to = ticket_task["assignedToName"]
        return assigned_to and not assigned_to.isspace() and assigned_to != "0"

    def _get_max_seconds_since_last_outage(self, edge: dict) -> int:
        from datetime import timezone

        tz_offset = edge["cached_info"]["site_details"]["tzOffset"]
        tz = timezone(timedelta(hours=tz_offset))
        now = datetime.now(tz=tz)

        last_outage_seconds = self._config.MONITOR_CONFIG["autoresolve"]["last_outage_seconds"]
        day_schedule = self._config.MONITOR_CONFIG["autoresolve"]["day_schedule"]
        day_start_hour = day_schedule["start_hour"]
        day_end_hour = day_schedule["end_hour"]

        if day_start_hour >= day_end_hour:
            day_end_hour += 24

        if day_start_hour <= now.hour < day_end_hour:
            return last_outage_seconds["day"]
        else:
            return last_outage_seconds["night"]

    def _get_notes_appended_since_latest_reopen_or_ticket_creation(self, ticket_notes: List[dict]) -> List[dict]:
        sorted_ticket_notes = sorted(ticket_notes, key=lambda note: note["createdDate"])
        latest_reopen = self._utils_repository.get_last_element_matching(
            sorted_ticket_notes, lambda note: REOPEN_NOTE_REGEX.search(note["noteValue"])
        )

        if not latest_reopen:
            # If there's no re-open, all notes in the ticket are the ones posted since the last outage
            return ticket_notes

        latest_reopen_position = ticket_notes.index(latest_reopen)
        return ticket_notes[latest_reopen_position:]

    def _get_triage_or_reopen_note(self, ticket_notes: List[dict]) -> Optional[dict]:
        return self._utils_repository.get_first_element_matching(
            ticket_notes,
            lambda note: TRIAGE_NOTE_REGEX.match(note["noteValue"]) or REOPEN_NOTE_REGEX.match(note["noteValue"]),
        )

    @staticmethod
    def _get_outage_type_from_ticket_notes(ticket_notes: List[dict]) -> Optional[str]:
        for note in ticket_notes:
            match = OUTAGE_TYPE_REGEX.search(note["noteValue"])
            if match:
                return match.group("outage_type")

    def _get_has_faulty_digi_link_from_ticket_notes(
        self, ticket_notes: List[dict], triage_note: Optional[dict]
    ) -> Optional[bool]:
        if not triage_note:
            return None

        digi_interfaces = set()

        for note in ticket_notes:
            match = DIGI_NOTE_REGEX.search(note["noteValue"])
            if match:
                interface = match.group("interface")
                digi_interfaces.add(interface)

        matches = LINK_INFO_REGEX.finditer(triage_note["noteValue"])

        for match in matches:
            link_interface = match.group("interface")
            link_status = match.group("status")

            if self._outage_repository.is_faulty_link(link_status):
                if link_interface in digi_interfaces:
                    return True

        return False

    async def _get_resolved_detailIds_service_numbers_and_interfaces(
        self, outage_ticket_id: int, ticket_detail_id: int, links: List[dict], details_from_ticket: List[dict]
    ) -> List[dict]:
        ticket_detailIds_mapped_to_interfaces_response = (
            await self._bruin_repository.
            get_ticket_detail_ids_by_ticket_detail_interfaces(
                outage_ticket_id, ticket_detail_id, links)
        )

        detailIds_service_numbers_and_interfaces = []
        if ticket_detailIds_mapped_to_interfaces_response["status"] not in range(200, 300):
            logger.error(
                f"Error while getting deailIds {outage_ticket_id} for details {ticket_detail_id} "
                f"and interfaces {links}: {ticket_detailIds_mapped_to_interfaces_response}"
            )
        else:
            detailIds_and_interfaces = (
                ticket_detailIds_mapped_to_interfaces_response["body"]["results"]
            )
            logger.info(f'Ticket detailIds and interfaces: {detailIds_and_interfaces}')
            detailIds_service_numbers_and_interfaces = [
                {
                    "detailId": detailId_and_interface["ticketDetailId"],
                    "interface": detailId_and_interface["interface"],
                    "service_number": self._get_service_number_for_detailId(
                        details_from_ticket, detailId_and_interface["ticketDetailId"])
                }
                for detailId_and_interface in detailIds_and_interfaces
                if detailId_and_interface["ticketDetailId"] != ticket_detail_id
            ]

            logger.info(f'Ticket details resolved interfaces count: '
                        f'{len(detailIds_service_numbers_and_interfaces)}')

        return detailIds_service_numbers_and_interfaces

    def _get_service_number_for_detailId(self, ticket_details: List[dict], detailId: int) -> str:
        for detail in ticket_details:
            if detail["detailID"] == detailId:
                return detail["detailValue"]

        return None

    def _get_link_access_types_from_affecting_trouble_note(
        self, interfaces: List[str], logical_id_list: List[dict]
    ) -> Optional[str]:
        if not interfaces:
            return None

        access_types = set()

        for interface in interfaces:
            link_access_type = [
                logical_id["access_type"]
                for logical_id in logical_id_list
                if logical_id["interface_name"] == interface
            ]
            if link_access_type:
                access_types.add(link_access_type[0])

        return list(access_types)

    def _is_ethernet_link_access_type(self, link_access_types: List[str]) -> bool:
        return (link_access_types
                and any([access_type for access_type in link_access_types if access_type == "Ethernet/T1/MPLS"]))

    def _get_has_faulty_byob_link_from_triage_note(self, triage_note: Optional[dict]) -> Optional[bool]:
        if not triage_note:
            return None

        matches = LINK_INFO_REGEX.finditer(triage_note["noteValue"])

        for match in matches:
            link_label = match.group("label")
            link_status = match.group("status")

            if self._outage_repository.is_faulty_link(link_status):
                if self._is_link_label_blacklisted_from_hnoc(link_label):
                    return True

        return False

    def _get_faulty_link_types_from_triage_note(self, triage_note: Optional[dict]) -> Optional[List[str]]:
        if not triage_note:
            return None

        link_types = set()
        matches = LINK_INFO_REGEX.finditer(triage_note["noteValue"])

        for match in matches:
            link_type = match.group("type")
            link_status = match.group("status")

            if self._outage_repository.is_faulty_link(link_status):
                link_types.add(link_type)

        return list(link_types)

    def _has_last_event_happened_recently(
        self,
        ticket_notes: list,
        documentation_cycle_start_date: str,
        max_seconds_since_last_event: int,
        note_regex: Pattern[str],
    ) -> bool:
        current_datetime = datetime.now(utc)

        notes_sorted_by_date_asc = sorted(ticket_notes, key=lambda note: note["createdDate"])
        last_event_note = self._utils_repository.get_last_element_matching(
            notes_sorted_by_date_asc, lambda note: note_regex.match(note["noteValue"])
        )
        if last_event_note:
            note_creation_date = parse(last_event_note["createdDate"]).astimezone(utc)
            seconds_elapsed_since_last_event = (current_datetime - note_creation_date).total_seconds()
            return seconds_elapsed_since_last_event <= max_seconds_since_last_event

        documentation_cycle_start_datetime = parse(documentation_cycle_start_date).replace(tzinfo=utc)
        seconds_elapsed_since_last_event = (current_datetime - documentation_cycle_start_datetime).total_seconds()
        return seconds_elapsed_since_last_event <= max_seconds_since_last_event

    async def _send_reminder(self, ticket_id: int, service_number: str, ticket_notes: list):
        logger.info(f"Attempting to send reminder for service number {service_number} to ticket {ticket_id}")

        filtered_notes = self._get_notes_appended_since_latest_reopen_or_ticket_creation(ticket_notes)
        last_documentation_cycle_start_date = filtered_notes[0]["createdDate"]

        max_seconds_since_last_reminder = self._config.MONITOR_CONFIG["wait_time_before_sending_new_milestone_reminder"]
        should_send_reminder_notification = not self._has_last_event_happened_recently(
            ticket_notes=filtered_notes,
            documentation_cycle_start_date=last_documentation_cycle_start_date,
            max_seconds_since_last_event=max_seconds_since_last_reminder,
            note_regex=REMINDER_NOTE_REGEX,
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

    async def _append_reminder_note(self, ticket_id: int, service_number: str):
        note_lines = ["#*MetTel's IPA*#", "Client Reminder"]
        reminder_note = os.linesep.join(note_lines)

        return await self._bruin_repository.append_note_to_ticket(
            ticket_id,
            reminder_note,
            service_numbers=[service_number],
        )

    async def _attempt_ticket_creation(self, edge: dict, outage_type: Outages):
        edge_status = edge["status"]
        edge_links = edge_status["links"]
        cached_edge = edge["cached_info"]
        serial_number = cached_edge["serial_number"]
        logical_id_list = cached_edge["logical_ids"]
        links_configuration = cached_edge["links_configuration"]
        client_id = cached_edge["bruin_client_info"]["client_id"]
        client_name = cached_edge["bruin_client_info"]["client_name"]
        is_edge_down = self._outage_repository.is_faulty_edge(edge_status["edgeState"])
        target_severity = self._get_target_severity(is_edge_down)
        has_faulty_digi_link = self._has_faulty_digi_link(edge_links, logical_id_list)
        has_faulty_byob_link = self._has_faulty_blacklisted_link(edge_links)
        faulty_link_types = self._get_faulty_link_types(edge_links, links_configuration)
        faulty_link_interfaces = self._get_faulty_link_interfaces(edge_links)

        logger.info(f"[{outage_type.value}] Attempting outage ticket creation for serial {serial_number}...")

        try:
            ticket_creation_response = await self._bruin_repository.create_outage_ticket(
                client_id, serial_number, faulty_link_interfaces)
            ticket_id = ticket_creation_response["body"]
            ticket_creation_response_status = ticket_creation_response["status"]
            logger.info(
                f"[{outage_type.value}] Bruin response for ticket creation for edge {edge}: "
                f"{ticket_creation_response}"
            )
            if ticket_creation_response_status in range(200, 300):
                logger.info(
                    f"[{outage_type.value}] Successfully created outage ticket for edge {edge}. Ticket ID: {ticket_id}"
                )
                self._metrics_repository.increment_tasks_created(
                    client=client_name,
                    outage_type=outage_type.value,
                    severity=target_severity,
                    has_digi=has_faulty_digi_link,
                    has_byob=has_faulty_byob_link,
                    link_types=faulty_link_types,
                )
                slack_message = (
                    f"Service Outage ticket created for edge {serial_number} in {outage_type.value} state: "
                    f"https://app.bruin.com/t/{ticket_id}."
                )
                await self._notifications_repository.send_slack_message(slack_message)
                await self._append_triage_note(ticket_id, cached_edge, edge_status, outage_type)
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=False,
                )

                if self._should_forward_to_hnoc(edge_links, is_edge_down):
                    logger.info(
                        f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
                        f"forwarded to the HNOC queue"
                    )
                    forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)
                    self._schedule_forward_to_hnoc_queue(
                        forward_time,
                        ticket_id,
                        serial_number,
                        client_name,
                        outage_type,
                        target_severity,
                        has_faulty_digi_link,
                        has_faulty_byob_link,
                        faulty_link_types,
                    )
                else:
                    logger.info(
                        f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
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
                        logger.error(
                            f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response["status"] not in range(200, 300):
                            logger.error(
                                f"Reminder note of edge {serial_number} could not be appended to ticket"
                                f" {ticket_id}!"
                            )

                if self._outage_repository.edge_has_all_links_down(edge["status"]):
                    logger.info(
                        f"Sending an email for ticket_id: {ticket_id} "
                        f"with serial: {serial_number} because all links are down..."
                    )
                    email_edge_fully_down = await self._bruin_repository.send_edge_is_down_email_notification(
                        ticket_id, serial_number)
                    if email_edge_fully_down["status"] not in range(200, 300):
                        logger.error(
                            f"Failed sending all links down email for ticket_id: {ticket_id} "
                            f"with serial: {serial_number}"
                        )

                await self._check_for_digi_reboot(ticket_id, logical_id_list, serial_number, edge_status)
            elif ticket_creation_response_status == 409:
                logger.info(
                    f"[{outage_type.value}] Faulty edge {serial_number} already has an outage ticket in "
                    f"progress (ID = {ticket_id}). Skipping outage ticket creation for "
                    "this edge..."
                )
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=True,
                )

                if self._should_forward_to_hnoc(edge_links, is_edge_down):
                    logger.info(
                        f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
                        f"forwarded to the HNOC queue"
                    )
                    forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)
                    self._schedule_forward_to_hnoc_queue(
                        forward_time,
                        ticket_id,
                        serial_number,
                        client_name,
                        outage_type,
                        target_severity,
                        has_faulty_digi_link,
                        has_faulty_byob_link,
                        faulty_link_types,
                    )
                else:
                    logger.info(
                        f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
                        f"should not be forwarded to HNOC. Skipping forward to HNOC..."
                    )
                    ticket_details = await self._bruin_repository.get_ticket_details(ticket_id)
                    ticket_notes = ticket_details["body"]["ticketNotes"]
                    await self._send_reminder(
                        ticket_id=ticket_id, service_number=serial_number, ticket_notes=ticket_notes
                    )

                await self._check_for_failed_digi_reboot(
                    ticket_id,
                    logical_id_list,
                    serial_number,
                    edge_status,
                    client_name,
                    outage_type,
                    target_severity,
                    has_faulty_digi_link,
                    has_faulty_byob_link,
                    faulty_link_types,
                )
                await self._attempt_forward_to_asr(
                    cached_edge,
                    edge_status,
                    ticket_id,
                    client_name,
                    outage_type,
                    target_severity,
                    has_faulty_digi_link,
                    has_faulty_byob_link,
                    faulty_link_types,
                )
            elif ticket_creation_response_status == 471:
                logger.info(
                    f"[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket "
                    f"(ID = {ticket_id}). Re-opening ticket..."
                )
                was_ticket_reopened = await self._reopen_outage_ticket(ticket_id, edge_status, cached_edge, outage_type)
                if was_ticket_reopened:
                    self._metrics_repository.increment_tasks_reopened(
                        client=client_name,
                        outage_type=outage_type.value,
                        severity=target_severity,
                        has_digi=has_faulty_digi_link,
                        has_byob=has_faulty_byob_link,
                        link_types=faulty_link_types,
                    )

                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=True,
                )

                if self._should_forward_to_hnoc(edge_links, is_edge_down):
                    logger.info(
                        f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
                        f"forwarded to the HNOC queue"
                    )
                    forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)
                    self._schedule_forward_to_hnoc_queue(
                        forward_time,
                        ticket_id,
                        serial_number,
                        client_name,
                        outage_type,
                        target_severity,
                        has_faulty_digi_link,
                        has_faulty_byob_link,
                        faulty_link_types,
                    )
                else:
                    logger.info(
                        f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
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
                        logger.error(
                            f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response["status"] not in range(200, 300):
                            logger.error(
                                f"Reminder note of edge {serial_number} could not be appended to ticket"
                                f" {ticket_id}!"
                            )

                await self._check_for_digi_reboot(ticket_id, logical_id_list, serial_number, edge_status)
            elif ticket_creation_response_status == 472:
                logger.info(
                    f"[{outage_type.value}] Faulty edge {serial_number} has a resolved outage ticket "
                    f"(ID = {ticket_id}). Its ticket detail was automatically unresolved "
                    f"by Bruin. Appending reopen note to ticket..."
                )
                self._metrics_repository.increment_tasks_reopened(
                    client=client_name,
                    outage_type=outage_type.value,
                    severity=target_severity,
                    has_digi=has_faulty_digi_link,
                    has_byob=has_faulty_byob_link,
                    link_types=faulty_link_types,
                )

                await self._append_triage_note(
                    ticket_id,
                    cached_edge,
                    edge_status,
                    outage_type,
                    is_reopen_note=True,
                )
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=True,
                )

                if self._should_forward_to_hnoc(edge_links, is_edge_down):
                    logger.info(
                        f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
                        f"forwarded to the HNOC queue"
                    )
                    forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)
                    self._schedule_forward_to_hnoc_queue(
                        forward_time,
                        ticket_id,
                        serial_number,
                        client_name,
                        outage_type,
                        target_severity,
                        has_faulty_digi_link,
                        has_faulty_byob_link,
                        faulty_link_types,
                    )
                else:
                    logger.info(
                        f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
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
                        logger.error(
                            f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response["status"] not in range(200, 300):
                            logger.error(
                                f"Reminder note of edge {serial_number} could not be appended to ticket"
                                f" {ticket_id}!"
                            )

            elif ticket_creation_response_status == 473:
                logger.info(
                    f"[{outage_type.value}] There is a resolve outage ticket for the same location of faulty "
                    f"edge {serial_number} (ticket ID = {ticket_id}). The ticket was "
                    f"automatically unresolved by Bruin and a new ticket detail for serial {serial_number} was "
                    f"appended to it. Appending initial triage note for this service number..."
                )
                self._metrics_repository.increment_tasks_reopened(
                    client=client_name,
                    outage_type=outage_type.value,
                    severity=target_severity,
                    has_digi=has_faulty_digi_link,
                    has_byob=has_faulty_byob_link,
                    link_types=faulty_link_types,
                )

                await self._append_triage_note(ticket_id, cached_edge, edge_status, outage_type)
                await self._change_ticket_severity(
                    ticket_id=ticket_id,
                    edge_status=edge_status,
                    target_severity=target_severity,
                    check_ticket_tasks=False,
                )

                if self._should_forward_to_hnoc(edge_links, is_edge_down):
                    logger.info(
                        f"[{outage_type.value}] Task from ticket {ticket_id} for edge {serial_number} must be "
                        f"forwarded to the HNOC queue"
                    )
                    forward_time = self._get_hnoc_forward_time_by_outage_type(outage_type, edge)
                    self._schedule_forward_to_hnoc_queue(
                        forward_time,
                        ticket_id,
                        serial_number,
                        client_name,
                        outage_type,
                        target_severity,
                        has_faulty_digi_link,
                        has_faulty_byob_link,
                        faulty_link_types,
                    )
                else:
                    logger.info(
                        f"Ticket_id: {ticket_id} for serial: {serial_number} "
                        f"with link_data: {edge_links} has a blacklisted link and "
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
                        logger.error(
                            f"Reminder email of edge {serial_number} could not be sent for ticket {ticket_id}!"
                        )
                    else:
                        append_note_response = await self._append_reminder_note(ticket_id, serial_number)
                        if append_note_response["status"] not in range(200, 300):
                            logger.error(
                                f"Reminder note of edge {serial_number} could not be appended to ticket"
                                f" {ticket_id}!"
                            )
        except Exception as ex:
            msg = f"Error while attempting ticket creation for edge {serial_number}: {ex}"
            raise Exception(msg)

    def _has_business_grade_link_down(self, links: List[dict]) -> bool:
        return any(
            link
            for link in links
            if link["displayName"] and self._is_business_grade_link_label(link["displayName"])
            if self._outage_repository.is_faulty_link(link["linkState"])
        )

    def _is_business_grade_link_label(self, label: str) -> bool:
        business_grade_link_labels = self._config.MONITOR_CONFIG["business_grade_link_labels"]
        return any(bg_label for bg_label in business_grade_link_labels if bg_label in label)
