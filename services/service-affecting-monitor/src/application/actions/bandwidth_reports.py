from datetime import datetime, timedelta

from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from application import AffectingTroubles


class BandwidthReports:

    def __init__(self, logger, scheduler, config, velocloud_repository, bruin_repository, trouble_repository,
                 customer_cache_repository, notifications_repository, utils_repository, template_repository):
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._velocloud_repository = velocloud_repository
        self._bruin_repository = bruin_repository
        self._trouble_repository = trouble_repository
        self._customer_cache_repository = customer_cache_repository
        self._notifications_repository = notifications_repository
        self._utils_repository = utils_repository
        self._template_repository = template_repository

    async def start_bandwidth_reports_job(self, exec_on_start=False):
        self._logger.info(f'Scheduled task: bandwidth reports')

        if exec_on_start:
            await self._bandwidth_reports_job()
        else:
            self._scheduler.add_job(self._bandwidth_reports_job,
                                    CronTrigger.from_crontab(self._config.BANDWIDTH_REPORT_CONFIG['crontab'],
                                                             timezone=timezone('UTC')),
                                    id='_bandwidth_reports', replace_existing=True)

    async def _bandwidth_reports_job(self):
        clients = self._config.BANDWIDTH_REPORT_CONFIG['clients']
        self._logger.info(f'Running bandwidth reports process for {len(clients)} client(s)')
        start = datetime.now()

        customer_cache_response = await self._customer_cache_repository.get_cache_for_affecting_monitoring()
        customer_cache = customer_cache_response['body']

        if customer_cache_response['status'] not in range(200, 300):
            self._logger.error('[bandwidth-reports] Error getting customer cache. Process cannot keep going.')
            return

        links_metrics_response = await self._velocloud_repository.get_links_metrics_for_bandwidth_reports()
        links_metrics = links_metrics_response['body']

        if links_metrics_response['status'] not in range(200, 300):
            self._logger.info('[bandwidth-reports] Error getting links metrics. Process cannot keep going.')
            return

        serial_numbers = set()
        client_names_by_id = {}

        for edge in customer_cache:
            serial_numbers.add(edge['serial_number'])
            client = edge['bruin_client_info']
            client_names_by_id[client['client_id']] = client['client_name']

        for client_id in clients:
            client_name = client_names_by_id[client_id]
            await self._generate_bandwidth_report_for_client(client_id, client_name, serial_numbers, links_metrics,
                                                             customer_cache)
            self._logger.info(f'[bandwidth-reports] Report for client {client_id} sent via email')

        end = datetime.now()
        self._logger.info(
            f'[bandwidth-reports] Report generation for all clients finished. '
            f'Took {round((end - start).total_seconds() / 60, 2)} minutes.'
        )

    async def _generate_bandwidth_report_for_client(self, client_id, client_name, serial_numbers, links_metrics,
                                                    customer_cache):
        start_date = self._get_start_date()
        end_date = self._get_end_date()

        tickets = await self._bruin_repository.get_affecting_ticket_for_report(client_id, start_date, end_date)

        if tickets is None:
            self._logger.error(f'[bandwidth-reports] Error getting tickets for client {client_id}. Skipping...')
            return

        ticket_details = self._bruin_repository.transform_tickets_into_ticket_details(tickets)
        ticket_details = self._bruin_repository.filter_ticket_details_by_serials(ticket_details, serial_numbers)
        ticket_details = self._bruin_repository.filter_trouble_notes_in_ticket_details(
            ticket_details,
            [AffectingTroubles.BANDWIDTH_OVER_UTILIZATION.value]
        )

        links_metrics = self._velocloud_repository.filter_links_metrics_by_client(links_metrics, client_id,
                                                                                  customer_cache)
        links_metrics = self._add_bandwidth_to_links_metrics(links_metrics)
        grouped_ticket_details = self._bruin_repository.group_ticket_details_by_serial_and_interface(ticket_details)
        report_items = self._bruin_repository.prepare_items_for_bandwidth_report(
            links_metrics, grouped_ticket_details
        )

        if self._config.BANDWIDTH_REPORT_CONFIG['environment'] != 'production':
            self._logger.info(f'[bandwidth-reports] No report will be sent for client {client_id} '
                              f'since the current environment is not production')
            return

        email = self._template_repository.compose_bandwidth_report_email(
            client_id=client_id,
            client_name=client_name,
            report_items=report_items,
        )

        if email:
            await self._notifications_repository.send_email(email_object=email)

    def _add_bandwidth_to_links_metrics(self, links_metrics):
        for link_metrics in links_metrics:
            lookup_interval_minutes = self._config.BANDWIDTH_REPORT_CONFIG['lookup_interval_hours'] * 60

            rx_bytes = link_metrics['bytesRx']
            tx_bytes = link_metrics['bytesTx']
            rx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(rx_bytes, lookup_interval_minutes)
            tx_throughput = self._trouble_repository.get_bandwidth_throughput_bps(tx_bytes, lookup_interval_minutes)

            average_bandwidth = (rx_throughput + tx_throughput) / 2
            link_metrics['avgBandwidth'] = self._utils_repository.humanize_bps(average_bandwidth)

        return links_metrics

    def _get_start_date(self):
        now = datetime.utcnow()
        start_date = now - timedelta(hours=self._config.BANDWIDTH_REPORT_CONFIG['lookup_interval_hours'])
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_date.isoformat() + 'Z'

    def _get_end_date(self):
        now = datetime.utcnow()
        end_date = now.replace(microsecond=0)
        return end_date.isoformat() + 'Z'
