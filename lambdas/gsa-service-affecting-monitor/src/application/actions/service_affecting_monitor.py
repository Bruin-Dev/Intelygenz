import asyncio
import time
from typing import List

from src.application import AffectingTroubles

customer_cache = []


class ServiceAffectingMonitor:
    def __init__(
        self,
        logger,
        config,
        velocloud_repository,
        notes_repository,
        trouble_repository,
        utils_repository,
        email_repository,
    ):
        self._logger = logger
        self._config = config
        self._velocloud_repository = velocloud_repository
        self._notes_repository = notes_repository
        self._trouble_repository = trouble_repository
        self._utils_repository = utils_repository
        self._email_repository = email_repository

    async def start_service_affecting_monitor(self):
        await self._service_affecting_monitor_process()

    async def _service_affecting_monitor_process(self):
        self._logger.info(f"Starting Service Affecting Monitor process now...")
        start_time = time.time()

        global customer_cache
        if not customer_cache:
            customer_cache = await self._velocloud_repository.get_all_edges()

        if not customer_cache:
            self._logger.info("Got an empty customer cache. Process cannot keep going.")
            return

        await self._latency_check()
        await self._packet_loss_check()
        await self._jitter_check()
        await self._bandwidth_check()
        await self._bouncing_check()

        self._logger.info(f"Finished processing all links! Took {round((time.time() - start_time) / 60, 2)} minutes")

    def _structure_links_metrics(self, links_metrics: list, events: dict = None) -> list:
        result = []

        for link_info in links_metrics:
            velocloud_host = link_info["link"]["host"]
            enterprise_name = link_info["link"]["enterpriseName"]
            enterprise_id = link_info["link"]["enterpriseId"]
            edge_state = link_info["link"]["edgeState"]

            if edge_state is None:
                self._logger.info(
                    f"Edge in host {velocloud_host} and enterprise {enterprise_name} (ID: {enterprise_id}) "
                    f"has an invalid state. Skipping..."
                )
                continue

            if edge_state == "NEVER_ACTIVATED":
                self._logger.info(
                    f"Edge {link_info['link']['edgeId']} in host {velocloud_host} and enterprise {enterprise_name}"
                    f"(ID: {enterprise_id}) has never been activated. Skipping..."
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

    async def _map_cached_edges_with_links_metrics(self, links_metrics: list) -> list:
        result = []

        cached_edges_by_serial = {elem["serial_number"]: elem for elem in customer_cache}

        for elem in links_metrics:
            serial_number = elem["edge_status"]["edgeSerialNumber"]
            cached_edge = cached_edges_by_serial.get(serial_number)
            if not cached_edge:
                self._logger.info(f"No cached info was found for edge {serial_number}. Skipping...")
                continue

            result.append(
                {
                    "cached_info": cached_edge,
                    **elem,
                }
            )

        return result

    @staticmethod
    def _group_links_by_edge(links: List[dict]) -> List[dict]:
        edge_info_by_serial = {}

        for link in links:
            serial_number = link["cached_info"]["serial_number"]

            edge_info = {
                "cached_info": link["cached_info"],
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

    async def _latency_check(self):
        self._logger.info("Looking for latency issues...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_latency_checks()
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking latency issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache = await self._map_cached_edges_with_links_metrics(links_metrics)

        for elem in metrics_with_cache:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]

            serial_number = cached_info["serial_number"]

            if self._trouble_repository.are_latency_metrics_within_threshold(metrics):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed latency thresholds"
                )
                continue

            await self._process_latency_trouble(elem)

        self._logger.info("Finished looking for latency issues!")

    async def _packet_loss_check(self):
        self._logger.info("Looking for packet loss issues...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_packet_loss_checks()
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking packet loss issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache = await self._map_cached_edges_with_links_metrics(links_metrics)

        for elem in metrics_with_cache:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]

            serial_number = cached_info["serial_number"]

            if self._trouble_repository.are_packet_loss_metrics_within_threshold(metrics):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed packet loss thresholds"
                )
                continue

            await self._process_packet_loss_trouble(elem)

        self._logger.info("Finished looking for packet loss issues!")

    async def _jitter_check(self):
        self._logger.info("Looking for jitter issues...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_jitter_checks()
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking jitter issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache = await self._map_cached_edges_with_links_metrics(links_metrics)

        for elem in metrics_with_cache:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]

            serial_number = cached_info["serial_number"]

            if self._trouble_repository.are_jitter_metrics_within_threshold(metrics):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed jitter thresholds"
                )
                continue

            await self._process_jitter_trouble(elem)

        self._logger.info("Finished looking for jitter issues!")

    async def _bandwidth_check(self):
        self._logger.info("Looking for bandwidth issues...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bandwidth_checks()
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking bandwidth issues. Skipping...")
            return

        links_metrics = self._structure_links_metrics(links_metrics)
        metrics_with_cache = await self._map_cached_edges_with_links_metrics(links_metrics)

        for elem in metrics_with_cache:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            metrics = elem["link_metrics"]

            tx_bandwidth = metrics["bpsOfBestPathTx"]
            rx_bandwidth = metrics["bpsOfBestPathRx"]

            is_tx_bandwidth_valid = self._trouble_repository.is_valid_bps_metric(tx_bandwidth)
            is_rx_bandwidth_valid = self._trouble_repository.is_valid_bps_metric(rx_bandwidth)

            serial_number = cached_info["serial_number"]
            trouble = AffectingTroubles.BANDWIDTH_OVER_UTILIZATION
            scan_interval = self._config.MONITOR_CONFIG["monitoring_minutes_per_trouble"][trouble]

            if is_tx_bandwidth_valid and is_rx_bandwidth_valid:
                within_threshold = self._trouble_repository.are_bandwidth_metrics_within_threshold(
                    metrics, scan_interval
                )
            elif is_tx_bandwidth_valid and not is_rx_bandwidth_valid:
                within_threshold = self._trouble_repository.is_bandwidth_tx_within_threshold(metrics, scan_interval)
            elif is_rx_bandwidth_valid and not is_tx_bandwidth_valid:
                within_threshold = self._trouble_repository.is_bandwidth_rx_within_threshold(metrics, scan_interval)
            else:
                continue

            if within_threshold:
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed any bandwidth thresholds"
                )
                continue

            await self._process_bandwidth_trouble(elem)

        self._logger.info("Finished looking for bandwidth issues!")

    async def _bouncing_check(self):
        self._logger.info("Looking for bouncing issues...")

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bouncing_checks()
        links_metrics: list = links_metrics_response["body"]

        if not links_metrics:
            self._logger.info("List of links arrived empty while checking bouncing issues. Skipping...")
            return

        events = await self._velocloud_repository.get_events_by_serial_and_interface(customer_cache)
        links_metrics = self._structure_links_metrics(links_metrics, events)
        metrics_with_cache = await self._map_cached_edges_with_links_metrics(links_metrics)

        for elem in metrics_with_cache:
            await asyncio.sleep(0)

            cached_info = elem["cached_info"]
            link_status = elem["link_status"]
            events = elem["link_events"]

            serial_number = cached_info["serial_number"]

            if not events:
                self._logger.info(
                    f"No events were found for {link_status['interface']} from {serial_number} "
                    f"while looking for bouncing troubles"
                )
                continue

            if self._trouble_repository.are_bouncing_events_within_threshold(events):
                self._logger.info(
                    f"Link {link_status['interface']} from {serial_number} didn't exceed bouncing thresholds"
                )
                continue

            await self._process_bouncing_trouble(elem)

        self._logger.info("Finished looking for bouncing issues!")

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
        await self._process_affecting_trouble(link_data, trouble)

    async def _process_affecting_trouble(self, link_data: dict, trouble: AffectingTroubles):
        serial_number = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]

        self._logger.info(
            f"Service Affecting trouble of type {trouble.value} detected in interface {interface} of edge "
            f"{serial_number}"
        )

        await self._report_trouble(link_data, trouble)

    async def _report_trouble(self, link_data: dict, trouble: AffectingTroubles):
        build_note_fn = self._notes_repository.get_build_note_fn_by_trouble(trouble)
        affecting_trouble_note = build_note_fn(link_data)

        serial = link_data["cached_info"]["serial_number"]
        interface = link_data["link_status"]["interface"]

        self._logger.info(
            f"Sending an email to report {trouble.value} trouble " f"on interface {interface} of edge {serial}"
        )

        email = {
            "subject": f"{trouble.value} detected on {serial} - {interface}",
            "recipient": self._config.EMAIL_CONFIG["recipient"],
            "text": "",
            "html": f"<pre>{affecting_trouble_note}</pre>",
            "images": [],
            "attachments": [],
        }

        working_environment = self._config.CURRENT_ENVIRONMENT
        if working_environment == "production":
            self._email_repository.send_to_email(email)
            self._logger.info(f"Email sent to report {trouble.value} trouble on interface {interface} of edge {serial}")
        else:
            self._logger.info(
                f"Email to report {trouble.value} trouble on interface {interface} of edge {serial} "
                f"won't be sent since the current environment is {working_environment.upper()}"
            )
