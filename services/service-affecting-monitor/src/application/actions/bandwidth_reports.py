import asyncio
import logging
import base64
from datetime import datetime, timedelta

from application import AffectingTroubles
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone, utc

logger = logging.getLogger(__name__)


class BandwidthReports:
    def __init__(
        self,
        scheduler,
        config,
        velocloud_repository,
        bruin_repository,
        trouble_repository,
        customer_cache_repository,
        email_repository,
        utils_repository,
        template_repository,
        metrics_repository,
        s3_repository,
    ):
        self._scheduler = scheduler
        self._config = config
        self._velocloud_repository = velocloud_repository
        self._bruin_repository = bruin_repository
        self._trouble_repository = trouble_repository
        self._customer_cache_repository = customer_cache_repository
        self._email_repository = email_repository
        self._utils_repository = utils_repository
        self._template_repository = template_repository
        self._metrics_repository = metrics_repository
        self._s3_repository = s3_repository

    async def start_bandwidth_reports_job(self, exec_on_start=False):
        logger.info(f"[bandwidth-reports] Scheduled task: bandwidth reports")

        if exec_on_start:
            await self._bandwidth_reports_job()

        cron = CronTrigger.from_crontab(
            self._config.BANDWIDTH_REPORT_CONFIG["crontab"], timezone=timezone(self._config.TIMEZONE)
        )
        self._scheduler.add_job(self._bandwidth_reports_job, cron, id="_bandwidth_reports", replace_existing=True)

    async def _bandwidth_reports_job(self):
        velocloud_host = self._config.VELOCLOUD_HOST
        clients_to_email = []
        if self._config.BANDWIDTH_REPORT_CONFIG["client_ids_by_host"].get(velocloud_host):
            clients_to_email = self._config.BANDWIDTH_REPORT_CONFIG["client_ids_by_host"][velocloud_host]

        logger.info(f"[bandwidth-reports] Running bandwidth reports process for all clients")
        logger.info(f"[bandwidth-reports] Emailing bandwidth reports to {len(clients_to_email)} clients")
        start = datetime.now()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        customer_cache_body = customer_cache_response["body"]

        if customer_cache_response["status"] not in range(200, 300) or customer_cache_response["status"] == 202:
            logger.error("[bandwidth-reports] Error getting customer cache. Process cannot keep going.")
            self._metrics_repository.increment_reports_signet_execution_KO()
            return

        enterprise_id_edge_id_relation = self.get_enterprise_id_and_edge_id_relation_from_customer_cache_response(
            customer_cache_body, velocloud_host
        )

        now = datetime.now(utc).replace(hour=5, minute=0, second=0, microsecond=0)
        interval_for_metrics = {
            "start": now - timedelta(hours=self._config.BANDWIDTH_REPORT_CONFIG["lookup_interval_hours"]),
            "end": now,
        }

        edge_links_metrics_response = await self._velocloud_repository.get_edge_link_series_for_bandwidth_reports(
            interval_for_metrics, enterprise_id_edge_id_relation
        )
        edge_links_metrics_response_body = edge_links_metrics_response["body"]

        if edge_links_metrics_response["status"] not in range(200, 300):
            logger.info("[bandwidth-reports] Error getting links metrics. Process cannot keep going.")
            self._metrics_repository.increment_reports_signet_execution_KO()
            return

        clients = set()
        client_names_by_id = {}

        for edge in customer_cache_body:
            client = edge["bruin_client_info"]
            clients.add(client["client_id"])
            client_names_by_id[client["client_id"]] = client["client_name"]

        logger.info(f"[bandwidth-reports] Generating bandwidth reports for {len(clients)} clients")

        for client_id in clients:
            client_name = client_names_by_id[client_id]
            should_email_report = client_id in clients_to_email
            serial_numbers = set([
                edge["serial_number"]
                for edge in customer_cache_body
                if edge["bruin_client_info"]["client_id"] == client_id
            ])
            await self._generate_bandwidth_report_for_client(
                client_id, client_name, serial_numbers, edge_links_metrics_response_body,
                enterprise_id_edge_id_relation, should_email_report
            )

        end = datetime.now()
        logger.info(
            f"[bandwidth-reports] Report generation for all {len(clients)} clients finished. "
            f"Took {round((end - start).total_seconds() / 60, 2)} minutes."
        )

    def get_enterprise_id_and_edge_id_relation_from_customer_cache_response(
        self, customer_cache_response_body, velocloud_host
    ):
        logger.info(f"[bandwidth-reports] Creating enterprise id edge id_relation list")
        enterprise_id_edge_id_relation = []
        for edge_info in customer_cache_response_body:

            if edge_info["edge"]["host"] == velocloud_host:
                enterprise_id_edge_id_relation.append(
                    {
                        "enterprise_id": edge_info["edge"]["enterprise_id"],
                        "enterprise_name": edge_info["edge"]["enterprise_name"],
                        "host": edge_info["edge"]["host"],
                        "edge_id": edge_info["edge"]["edge_id"],
                        "serial_number": edge_info["serial_number"],
                        "edge_name": edge_info["edge_name"],
                    }
                )

        return enterprise_id_edge_id_relation

    async def _generate_bandwidth_report_for_client(self, client_id, client_name, serial_numbers, links_metrics,
                                                    enterprise_id_edge_id_relation, should_email_report):
        logger.info(f"[bandwidth-reports] Generating bandwidth report for client id {client_id} and \
                      client name {client_name}, serial numbers {len(serial_numbers)}, {serial_numbers}")
        start_date = self._get_start_date()
        end_date = self._get_end_date()

        tickets = await self._bruin_repository.get_affecting_ticket_for_report(client_id, start_date, end_date)

        if tickets is None:
            logger.error(f"[bandwidth-reports] Error getting tickets for client {client_id}. Skipping...")
            self._metrics_repository.increment_reports_signet_execution_KO()
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

        report_items = self._bruin_repository.prepare_items_for_bandwidth_report(
            links_metrics, grouped_ticket_details, enterprise_id_edge_id_relation, serial_numbers)
        report_items.sort(key=lambda item: (item["serial_number"], item["interface"]))

        if self._config.CURRENT_ENVIRONMENT != "production":
            logger.info(
                f"[bandwidth-reports] No report will be sent for client {client_id} "
                f"since the current environment is not production"
            )
            return

        email = self._template_repository.compose_bandwidth_report_email(
            client_id=client_id,
            client_name=client_name,
            report_items=report_items,
        )

        if should_email_report:
            if email:
                logger.info(self._config.BANDWIDTH_REPORT_CONFIG["recipients"])
                await self._email_repository.send_email(email_object=email)
                self._metrics_repository.increment_reports_signet_execution_OK()
                logger.info(f"[bandwidth-reports] Report for client {client_id} sent via email")
            else:
                logger.error(f"[bandwidth-reports] No report for client {client_id} was sent via email")
                return

        csv_attachment = next(iter(email["body"]["email_data"]["attachments"]), None)
        if (csv_attachment):
            file_name = csv_attachment["name"]
            logger.info(f'[bandwidth-reports] Csv attachment {file_name} found')

            file_name_split = file_name.split(".")
            file_name_and_client_id = f'{file_name_split[0]}_{client_id}.{file_name_split[1]}'

            csv_content = base64.b64decode(csv_attachment["data"]).decode("utf-8")
            logger.info(f'[bandwidth-reports] Uploading csv attachment {file_name_and_client_id} to S3')

            s3_response_code = self._s3_repository.upload_file_to_s3(file_name_and_client_id, csv_content)
            if (s3_response_code != 200):
                logger.error(f'[bandwidth-reports] Csv attachment {file_name_and_client_id} not sent to S3')
            else:
                logger.info(f'[bandwidth-reports] Csv attachment {file_name_and_client_id} sent to S3')

    @staticmethod
    def find_metric_by_field_value(value, metrics):
        for metric in metrics:
            if value in metric.values():
                return metric

    def _add_bandwidth_to_links_metrics(self, links_metrics):
        logger.info(f"[bandwidth-reports] Adding bandwidth data to link metrics")
        reported_metrics = []
        for link_metric in links_metrics:
            logger.info(f"[bandwidth-report] Adding bandwidth data for edge {link_metric['serial_number']} and \
                interface {link_metric['link']['interface']} and \
                link name {link_metric['link']['displayName']}")
            down_bytes_metrics = self.find_metric_by_field_value("bytesRx", link_metric["series"])
            up_bytes_metrics = self.find_metric_by_field_value("bytesTx", link_metric["series"])
            down_bps_metrics = self.find_metric_by_field_value("bpsOfBestPathRx", link_metric["series"])
            up_bps_metrics = self.find_metric_by_field_value("bpsOfBestPathTx", link_metric["series"])

            down_bytes_metrics_time = down_bytes_metrics["tickInterval"] / 1000
            up_bytes_metrics_time = up_bytes_metrics["tickInterval"] / 1000

            down_bps_total_min = down_bps_metrics["min"]
            down_bps_total_max = down_bps_metrics["max"]

            up_bps_total_min = up_bps_metrics["min"]
            up_bps_total_max = up_bps_metrics["max"]

            peak_bytes_down = down_bytes_metrics["max"]
            peak_bytes_up = up_bytes_metrics["max"]

            timezone_default = utc
            timezone_config = timezone(self._config.TIMEZONE)

            start_time = timezone_default.localize(
                datetime.utcfromtimestamp(down_bytes_metrics["startTime"] / 1e3)
            ).astimezone(timezone_config)
            bandwidth_down_data_list = down_bytes_metrics["data"]
            bandwidth_up_data_list = up_bytes_metrics["data"]

            peak_time_down = start_time + timedelta(seconds=(down_bytes_metrics_time * bandwidth_down_data_list.index(
                                                    peak_bytes_down)))
            peak_time_up = start_time + timedelta(seconds=(up_bytes_metrics_time * bandwidth_up_data_list.index(
                                                  peak_bytes_up)))

            peak_bps_down = self._utils_repository.convert_bytes_to_bps(peak_bytes_down, down_bytes_metrics_time)
            peak_bps_up = self._utils_repository.convert_bytes_to_bps(peak_bytes_up, up_bytes_metrics_time)

            peak_percent_down = round((peak_bps_down * 100) / down_bps_total_min if down_bps_total_min > 0 else 0.0, 2)
            peak_percent_up = round((peak_bps_up * 100) / up_bps_total_min if up_bps_total_min > 0 else 0.0, 2)

            reported_metrics.append(
                {
                    "down_Mbps_total_min": self._utils_repository.humanize_bps_for_bandwidth_report(down_bps_total_min),
                    "down_Mbps_total_max": self._utils_repository.humanize_bps_for_bandwidth_report(down_bps_total_max),
                    "up_Mbps_total_min": self._utils_repository.humanize_bps_for_bandwidth_report(up_bps_total_min),
                    "up_Mbps_total_max": self._utils_repository.humanize_bps_for_bandwidth_report(up_bps_total_max),
                    "peak_Mbps_down": self._utils_repository.humanize_bps_for_bandwidth_report(peak_bps_down),
                    "peak_Mbps_up": self._utils_repository.humanize_bps_for_bandwidth_report(peak_bps_up),
                    "peak_percent_down": peak_percent_down,
                    "peak_percent_up": peak_percent_up,
                    "peak_time_down": peak_time_down.strftime("%I:%M %p EST"),
                    "peak_time_up": peak_time_up.strftime("%I:%M %p EST"),
                    "serial_number": link_metric["serial_number"],
                    "edge_name": link_metric["edge_name"],
                    "interface": link_metric["link"]["interface"],
                    "link_name": link_metric["link"]["displayName"],
                }
            )

        return reported_metrics

    def _get_start_date(self):
        now = datetime.utcnow().replace(hour=5, minute=0, second=0, microsecond=0)
        start_date = now - timedelta(hours=self._config.BANDWIDTH_REPORT_CONFIG["lookup_interval_hours"])
        return start_date.isoformat() + "Z"

    def _get_end_date(self):
        end_date = datetime.utcnow().replace(hour=5, minute=0, second=0, microsecond=0)
        return end_date.isoformat() + "Z"
