import asyncio
from datetime import datetime, timedelta

from application import AffectingTroubles
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone, utc


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

        tz = self._config.TIMEZONE
        cron = CronTrigger.from_crontab(self._config.BANDWIDTH_REPORT_CONFIG["crontab"], timezone=timezone(tz))
        self._scheduler.add_job(self._bandwidth_reports_job, cron, id="_bandwidth_reports", replace_existing=True)

    async def _bandwidth_reports_job(self):
        velocloud_host = self._config.VELOCLOUD_HOST
        clients = self._config.BANDWIDTH_REPORT_CONFIG["client_ids_by_host"][velocloud_host]
        self._logger.info(f"Running bandwidth reports process for {len(clients)} client(s)")
        start = datetime.now()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        customer_cache_body = customer_cache_response["body"]

        if customer_cache_response["status"] not in range(200, 300) or customer_cache_response["status"] == 202:
            self._logger.error("[bandwidth-reports] Error getting customer cache. Process cannot keep going.")
            return
        enterprise_id_edge_id_relation = self.get_enterprise_id_and_edge_id_relation_from_customer_cache_response(
            customer_cache_body, clients, velocloud_host)

        now = datetime.now(utc)
        interval_for_metrics = {
            "start": now - timedelta(hours=self._config.BANDWIDTH_REPORT_CONFIG["lookup_interval_hours"]),
            "end": now,
        }

        edge_links_metrics_response = await self._velocloud_repository.get_edge_link_series_for_bandwidth_reports(
            interval_for_metrics,
            enterprise_id_edge_id_relation)
        edge_links_metrics_response_body = edge_links_metrics_response["body"]

        if edge_links_metrics_response["status"] not in range(200, 300):
            self._logger.info("[bandwidth-reports] Error getting links metrics. Process cannot keep going.")
            return

        serial_numbers = set()
        client_names_by_id = {}

        for edge in customer_cache_body:
            serial_numbers.add(edge["serial_number"])
            client = edge["bruin_client_info"]
            client_names_by_id[client["client_id"]] = client["client_name"]

        for client_id in clients:
            client_name = client_names_by_id[client_id]
            await self._generate_bandwidth_report_for_client(
                client_id, client_name, serial_numbers, edge_links_metrics_response_body
            )

        end = datetime.now()
        self._logger.info(
            f"[bandwidth-reports] Report generation for all clients finished. "
            f"Took {round((end - start).total_seconds() / 60, 2)} minutes."
        )

    def get_enterprise_id_and_edge_id_relation_from_customer_cache_response(self,
                                                                            customer_cache_response_body,
                                                                            clients_id,
                                                                            velocloud_host):
        enterprise_id_edge_id_relation = []
        for edge_info in customer_cache_response_body:

            if edge_info['edge']['host'] == velocloud_host and \
                    edge_info['bruin_client_info']['client_id'] in clients_id:
                enterprise_id_edge_id_relation.append(
                    {'enterprise_id': edge_info['edge']['enterprise_id'],
                     'host': edge_info['edge']['host'],
                     'edge_id': edge_info['edge']['edge_id'],
                     'serial_number': edge_info['serial_number'],
                     'edge_name': edge_info['edge_name']
                     }
                )

        return enterprise_id_edge_id_relation

    async def _generate_bandwidth_report_for_client(
            self, client_id, client_name, serial_numbers, links_metrics
    ):
        start_date = self._get_start_date()
        end_date = self._get_end_date()

        tickets = await self._bruin_repository.get_affecting_ticket_for_report(client_id, start_date, end_date)

        if tickets is None:
            self._logger.error(f"[bandwidth-reports] Error getting tickets for client {client_id}. Skipping...")
            return

        ticket_details = self._bruin_repository.transform_tickets_into_ticket_details(tickets)
        ticket_details = self._bruin_repository.filter_ticket_details_by_serials(ticket_details, serial_numbers)
        ticket_details = self._bruin_repository.filter_trouble_notes_in_ticket_details(
            ticket_details, [AffectingTroubles.BANDWIDTH_OVER_UTILIZATION.value]
        )
        await asyncio.sleep(0)

        links_metrics = self._add_bandwidth_to_links_metrics(links_metrics)
        grouped_ticket_details = self._bruin_repository.group_ticket_details_by_serial_and_interface(ticket_details)
        await asyncio.sleep(0)

        report_items = self._bruin_repository.prepare_items_for_bandwidth_report(links_metrics, grouped_ticket_details)
        report_items.sort(key=lambda item: (item["serial_number"], item["interface"]))

        if self._config.CURRENT_ENVIRONMENT != "production":
            self._logger.info(
                f"[bandwidth-reports] No report will be sent for client {client_id} "
                f"since the current environment is not production"
            )
            return

        email = self._template_repository.compose_bandwidth_report_email(
            client_id=client_id,
            client_name=client_name,
            report_items=report_items,
        )

        if email:
            await self._email_repository.send_email(email_object=email)
            self._logger.info(f"[bandwidth-reports] Report for client {client_id} sent via email")

    @staticmethod
    def find_metric_by_field_value(value, metrics):
        for metric in metrics:
            if value in metric.values():
                return metric

    def _add_bandwidth_to_links_metrics(self, links_metrics):
        reported_metrics = []
        for link_metric in links_metrics:
            down_bytes_metrics = self.find_metric_by_field_value('bytesRx', link_metric['series'])
            up_bytes_metrics = self.find_metric_by_field_value('bytesTx', link_metric['series'])
            down_bytes_total = down_bytes_metrics['total']
            up_bytes_total = up_bytes_metrics["total"]

            measured_bandwidth_down = self.find_metric_by_field_value('bpsOfBestPathRx', link_metric['series'])['max']
            measured_bandwidth_up = self.find_metric_by_field_value('bpsOfBestPathTx', link_metric['series'])['max']

            peak_bytes_down = down_bytes_metrics["max"]
            peak_bytes_up = up_bytes_metrics["max"]

            average_bandwidth = (down_bytes_total + up_bytes_total) / 2
            # Percentages on peaks with measured_bandwidth_down
            # peak_percent_down = (peak_bytes_down * 100) / \
            #                     measured_bandwidth_down if measured_bandwidth_down > 0 else 0.0
            # peak_percent_up = (peak_bytes_up * 100) / \
            #                   measured_bandwidth_up if measured_bandwidth_up > 0 else 0.0

            # Percentages on peaks with totals
            peak_percent_down = round((peak_bytes_down * 100) / down_bytes_total if down_bytes_total > 0 else 0.0, 2)
            peak_percent_up = round((peak_bytes_up * 100) / up_bytes_total if up_bytes_total > 0 else 0.0, 2)

            reported_metrics.append(
                {
                    "down_bytes_total": self._utils_repository.humanize_bps(down_bytes_total),
                    "up_bytes_total": self._utils_repository.humanize_bps(up_bytes_total),
                    "measured_bandwidth_down": self._utils_repository.humanize_bps(measured_bandwidth_down),
                    "measured_bandwidth_up": self._utils_repository.humanize_bps(measured_bandwidth_up),
                    "peak_bytes_down": self._utils_repository.humanize_bps(peak_bytes_down),
                    "peak_bytes_up": self._utils_repository.humanize_bps(peak_bytes_up),
                    "peak_percent_down": peak_percent_down,
                    "peak_percent_up": peak_percent_up,
                    "average_bandwidth": self._utils_repository.humanize_bps(average_bandwidth),
                    "serial_number": link_metric['serial_number'],
                    "edge_name": link_metric['edge_name'],
                    "interface": link_metric['link']['interface']
                }
            )

        return reported_metrics

    def _get_start_date(self):
        now = datetime.utcnow()
        start_date = now - timedelta(hours=self._config.BANDWIDTH_REPORT_CONFIG["lookup_interval_hours"])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_date.isoformat() + "Z"

    def _get_end_date(self):
        now = datetime.utcnow()
        end_date = now.replace(microsecond=0)
        return end_date.isoformat() + "Z"
