import asyncio
from datetime import datetime, timedelta

from application import AffectingTroubles
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone


class BandwidthReports:
    def __init__(
        self,
        logger,
        scheduler,
        config,
        velocloud_repository,
        bruin_repository,
        trouble_repository,
        customer_cache_repository,
        email_repository,
        utils_repository,
        template_repository,
    ):
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._velocloud_repository = velocloud_repository
        self._bruin_repository = bruin_repository
        self._trouble_repository = trouble_repository
        self._customer_cache_repository = customer_cache_repository
        self._email_repository = email_repository
        self._utils_repository = utils_repository
        self._template_repository = template_repository

    async def start_bandwidth_reports_job(self, exec_on_start=False):
        self._logger.info(f"Scheduled task: bandwidth reports")

        if exec_on_start:
            await self._bandwidth_reports_job()

        cron = CronTrigger.from_crontab(
            self._config.BANDWIDTH_REPORT_CONFIG["crontab"], timezone=timezone(self._config.TIMEZONE)
        )
        self._scheduler.add_job(self._bandwidth_reports_job, cron, id="_bandwidth_reports", replace_existing=True)

    async def _bandwidth_reports_job(self):
        bandwidth_report_init_time = datetime.utcnow()
        host = self._config.VELOCLOUD_HOST
        clients = self._config.BANDWIDTH_REPORT_CONFIG["client_ids_by_host"][host]
        self._logger.info(f"Running bandwidth reports process for {len(clients)} client(s)")

        rounded_now = self.get_rounded_date(datetime.utcnow())

        customer_cache_response = await self._customer_cache_repository.get_cache(
            velo_filter=self._config.MONITOR_CONFIG["velo_filter"]
        )
        customer_cache = customer_cache_response["body"]

        if customer_cache_response["status"] not in range(200, 300) or customer_cache_response["status"] == 202:
            self._logger.error("[bandwidth-reports] Error getting customer cache. Process cannot keep going.")
            return

        interval_for_metrics = self._velocloud_repository.get_interval_for_bandwidth_reports(rounded_now)
        links_metrics_response = await self._velocloud_repository.get_links_metrics_by_host(
            host=host, interval=interval_for_metrics
        )
        links_metrics = links_metrics_response["body"]

        if links_metrics_response["status"] not in range(200, 300):
            self._logger.info("[bandwidth-reports] Error getting links metrics. Process cannot keep going.")
            return

        serial_numbers = await self.get_serials_by_client_id(clients, customer_cache)

        client_names_by_id = await self.get_clients_names_and_ids_for_client(clients, customer_cache)

        for client_id in clients:
            await self._generate_bandwidth_report_for_client(
                client_id=client_id,
                client_name=client_names_by_id[client_id],
                serial_numbers=serial_numbers[client_id],
                links_metrics=links_metrics,
                customer_cache=customer_cache,
                interval_for_metrics=interval_for_metrics,
            )

        bandwidth_report_end_time = datetime.utcnow()
        self._logger.info(
            f"[bandwidth-reports] Report generation for all clients finished. "
            f"Took {round((bandwidth_report_end_time - bandwidth_report_init_time).total_seconds() / 60, 2)} minutes."
        )

    @staticmethod
    async def get_clients_names_and_ids_for_client(clients, customer_cache):
        client_names_by_id = {}
        for edge in customer_cache:
            client = edge["bruin_client_info"]
            client_id = client["client_id"]
            if client_id in clients:
                client_names_by_id[client["client_id"]] = client["client_name"]
        return client_names_by_id

    async def get_serials_by_client_id(self, clients, customer_cache):
        serial_by_client_id = self.initialize_serials_by_client(clients)
        for edge in customer_cache:
            serial_number = edge["serial_number"]
            client_id = edge["bruin_client_info"]["client_id"]
            if (
                client_id in serial_by_client_id
                and serial_number not in serial_by_client_id[edge["bruin_client_info"]["client_id"]]
            ):
                serial_by_client_id[client_id].append(serial_number)
        return serial_by_client_id

    @staticmethod
    def initialize_serials_by_client(clients):
        serial_by_client_id = {}
        for client in clients:
            serial_by_client_id[client] = []
        return serial_by_client_id

    async def _generate_bandwidth_report_for_client(
        self, client_id, client_name, serial_numbers, links_metrics, customer_cache, interval_for_metrics
    ):

        tickets = await self._bruin_repository.get_affecting_ticket_for_report(
            client_id, interval_for_metrics["start"], interval_for_metrics["end"]
        )

        ticket_details = await self.get_ticket_details_for_serial_and_trouble(serial_numbers, tickets)

        await asyncio.sleep(0)

        if ticket_details:
            links_metrics = self._velocloud_repository.filter_links_metrics_by_client(
                links_metrics, client_id, customer_cache
            )
            links_metrics = self._add_bandwidth_to_links_metrics(links_metrics)
            grouped_ticket_details = self._bruin_repository.group_ticket_details_by_serial_and_interface(ticket_details)
            await asyncio.sleep(0)

            report_items = self._bruin_repository.prepare_items_for_bandwidth_report(
                links_metrics, grouped_ticket_details
            )
            report_items.sort(key=lambda item: (item["serial_number"], item["interface"]))
        else:
            report_items = []

        if self._config.CURRENT_ENVIRONMENT != "production":
            self._logger.info(
                f"[bandwidth-reports] No report will be sent for client {client_id} "
                f"since the current environment is not production"
            )
            return

        await self._email_repository.send_email(
            email_object=self._template_repository.compose_bandwidth_report_email(
                client_id=client_id,
                client_name=client_name,
                report_items=report_items,
                interval_for_metrics=interval_for_metrics,
            )
        )
        self._logger.info(f"[bandwidth-reports] Report for client {client_id} sent via email")

    async def get_ticket_details_for_serial_and_trouble(self, serial_numbers, tickets):
        ticket_details = self._bruin_repository.transform_tickets_into_ticket_details(tickets)
        ticket_details = self._bruin_repository.filter_ticket_details_by_serials(ticket_details, serial_numbers)
        ticket_details = self._bruin_repository.filter_trouble_notes_in_ticket_details(
            ticket_details, [AffectingTroubles.BANDWIDTH_OVER_UTILIZATION.value]
        )
        return ticket_details

    def _add_bandwidth_to_links_metrics(self, links_metrics):
        for link_metrics in links_metrics:
            lookup_interval_minutes = self._config.BANDWIDTH_REPORT_CONFIG["lookup_interval_hours"] * 60

            rx_bytes = link_metrics["bytesRx"]
            tx_bytes = link_metrics["bytesTx"]
            rx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(rx_bytes, lookup_interval_minutes)
            tx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(tx_bytes, lookup_interval_minutes)

            average_bandwidth = (rx_throughput + tx_throughput) / 2
            link_metrics["avgBandwidth"] = self._utils_repository.humanize_bps(average_bandwidth)

        return links_metrics

    @staticmethod
    def get_rounded_date(date):
        return date.replace(hour=0, minute=0, second=0, microsecond=0)
