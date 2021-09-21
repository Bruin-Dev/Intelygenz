import asyncio
import time
from collections import defaultdict

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class RepairTicketsMonitor:
    def __init__(self, event_bus, logger, scheduler, config, repair_tickets_repository,
                 repair_tickets_kre_repository, bruin_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._repair_tickets_repository = repair_tickets_repository
        self._repair_tickets_kre_repository = repair_tickets_kre_repository

        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG['semaphores']['repair_tickets_concurrent'])

    async def start_repair_tickets_monitor(self, exec_on_start=False):
        self._logger.info('Scheduling RepairTicketsMonitor feedback job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info('RepairTicketsMonitor feedback job is going to be executed immediately')

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG['scheduler_config']['repair_ticket_seconds']
            self._scheduler.add_job(self._run_repair_tickets_polling, 'interval', seconds=scheduler_seconds,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_repair_tickets_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of repair tickets monitor job. Reason: {conflict}')

    async def _run_repair_tickets_polling(self):
        self._logger.info('Starting RepairTicketsMonitor feedback process...')

        start_time = time.time()

        self._logger.info('Getting all repair emails...')
        repair_emails = self._repair_tickets_repository.get_pending_repair_emails()
        self._logger.info(f'Got {len(repair_emails)} repair emails.')

        tasks = [
            self._process_repair_email(email_data)
            for email_data in repair_emails
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("RepairTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

    async def _process_repair_email(self, email_data: dict):
        # TODO: define the new logic
        email_id = email_data["email"]["email_id"]
        client_id = email_data["email"]["client_id"]
        parent_id = email_data["email"].get("parent_id", None)
        tag = email_data["tag"]
        tag_mock = {'tag_id': 0, 'confidence': 1.0}

        async with self._semaphore:
            prediction_response = await self._repair_tickets_kre_repository.get_prediction(email_data, tag)

            if prediction_response["status"] not in range(200, 300):
                self._logger.info(f"Error predicion response status code {prediction_response['status']}")
                return
            prediction = prediction_response.get('body')

            contact_info_by_site_id = defaultdict(dict)

            for service_number in prediction['service_numbers']:
                client_info_response = await self._bruin_repository.get_client_info(client_id, service_number)
                if client_info_response['status'] not in range(200, 300):
                    self._logger.info("TODO: error")
                    continue

                client_info = client_info_response.get('body', [])
                if not client_info:
                    self._logger.info("TODO: err, empty body for site id")
                    continue

                # TODO: check where to get the first site id
                client_info = client_info[0]
                site_id = client_info['site_id']

                contact_info_response = self._bruin_repository.get_site(client_id, site_id)
                site_contact_info = {
                    "name": contact_info_response['body']["primaryContactName"],
                    "phone": contact_info_response['body']["primaryContactPhone"],
                    "email": contact_info_response['body']["primaryContactEmail"]
                }

                # TODO: check if the contact info is filled, otherwise don't created the ticket
                #  or created with other endpoint info
                ticket_contact_info = {}  # ???

                contact_info_by_site_id[site_id]['site_contact_info'] = site_contact_info
                if 'service_numbers' not in contact_info_by_site_id[site_id]:
                    contact_info_by_site_id[site_id]['service_numbers'] = []
                contact_info_by_site_id[site_id]['service_numbers'].append(service_number)

            self._logger.info(f"email_id: {email_id} client_id: {client_id} prediction class "
                              f"{prediction_response['prediction_class']}")

            for site_id, data in contact_info_by_site_id.items():
                site_contact_info = data['site_contact_info']
                service_numbers = data['service_numbers']

                if prediction_response['prediction_class'] == 'VOO':
                    self._logger.info("TODO: create ticket for VOO or VAS ???")
                    if prediction['above_threshold'] and not prediction['in_validation_set']:

                        create_outage_ticket_response = self._bruin_repository.create_outage_ticket(
                            client_id, service_numbers, site_contact_info)
                        if create_outage_ticket_response['status'] not in range(200, 300):
                            self._logger.error('TODO: error creating voo ticket')

                        self._logger.info(
                            f"VOO Ticket created for client_id {client_id} and service_number {service_number} - "
                            f"{create_outage_ticket_response.get('body')}")
                elif prediction_response['prediction_class'] == 'VAS':
                    self._logger.info("TODO: create ticket for VOO or VAS ???")
                    if prediction['above_threshold'] and not prediction['in_validation_set']:

                        create_outage_ticket_response = self._bruin_repository.create_affecting_ticket(
                            client_id, service_numbers, site_contact_info)
                        if create_outage_ticket_response['status'] not in range(200, 300):
                            self._logger.error('TODO: error creating vas ticket')

                        self._logger.info(
                            f"VAS Ticket created for client_id {client_id} and service_number {service_number} - "
                            f"{create_outage_ticket_response.get('body')}")

            # self._repair_tickets_kre_repository.save_predictions(
            #     client_id, site_id, service_number, site_contact_info, prediction)

            # Remove from DB
            # self._repair_tickets_repository.mark_complete(email_id)
