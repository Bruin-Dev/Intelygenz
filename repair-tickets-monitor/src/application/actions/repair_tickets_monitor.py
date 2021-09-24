import asyncio
import time
from collections import defaultdict

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class RepairTicketsMonitor:
    def __init__(
        self,
        event_bus,
        logger,
        scheduler,
        config,
        repair_tickets_repository,
        repair_tickets_kre_repository,
        bruin_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._repair_tickets_repository = repair_tickets_repository
        self._repair_tickets_kre_repository = repair_tickets_kre_repository

        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG["semaphores"]["repair_tickets_concurrent"]
        )

    async def start_repair_tickets_monitor(self, exec_on_start=False):
        self._logger.info("Scheduling RepairTicketsMonitor feedback job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info(
                "RepairTicketsMonitor feedback job is going to be executed immediately"
            )

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"][
                "repair_ticket_seconds"
            ]
            self._scheduler.add_job(
                self._run_repair_tickets_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_repair_tickets_polling",
            )
        except ConflictingIdError as conflict:
            self._logger.info(
                f"Skipping start of repair tickets monitor job. Reason: {conflict}"
            )

    async def _run_repair_tickets_polling(self):
        self._logger.info("Starting RepairTicketsMonitor feedback process...")

        start_time = time.time()

        self._logger.info("Getting all repair emails...")
        repair_emails = self._repair_tickets_repository.get_pending_repair_emails()
        self._logger.info(f"Got {len(repair_emails)} repair emails.")

        tasks = [self._process_repair_email(email_data) for email_data in repair_emails]
        output = await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info(
            "RepairTicketsMonitor process finished! Took {:.3f}s".format(
                time.time() - start_time
            )
        )
        self._logger.info(f"Output: {output}")

    async def _get_prediction(self, email_data):
        prediction_response = await self._repair_tickets_kre_repository.get_prediction(
            email_data
        )
        if prediction_response["status"] not in range(200, 300):
            self._logger.info(
                f"Error predicion response status code {prediction_response['status']}"
            )
            return
        return prediction_response.get("body")

    async def _get_client_info(self, client_id, service_number):
        client_info_response = await self._bruin_repository.get_client_info(
            client_id, service_number
        )
        if client_info_response["status"] not in range(200, 300):
            self._logger.info(
                f"Error retrieving client_info from Bruin for client_id={client_id} with service_number={service_number}"
            )
            return None

        client_info = client_info_response.get("body", [])
        if not client_info:
            self._logger.info(
                f"Empty body when retrieving client_info from Bruin for client_id={client_id} with service_number={service_number}"
            )
            return None

        return client_info

    def _get_site_contact_info(self, client_id, site_id):
        response = self._bruin_repository.get_site(client_id, site_id)
        contact_info = response["body"]

        if len(contact_info) > 1:
            self._logger.warning(
                "Contact Info response contains more than one element. Using just the first one."
            )

        contact_info = contact_info[0]

        site_contact_info = {
            "name": contact_info["primaryContactName"],
            "phone": contact_info["primaryContactPhone"],
            "email": contact_info["primaryContactEmail"],
        }

        return site_contact_info

    def _update_contactinfo_dict(
        self, contact_info_dict, site_id, site_contact_info, service_number
    ):
        contact_info = contact_info_dict[site_id]
        if "service_numbers" not in contact_info:
            contact_info["service_numbers"] = []

        contact_info["site_contact_info"] = site_contact_info
        contact_info["service_numbers"].append(service_number)
        contact_info_dict[site_id] = contact_info
        return contact_info_dict

    async def _get_definitive_contact_infos(self, client_id, prediction):
        contact_info_dict = defaultdict(dict)
        potential_service_numbers = prediction["potential_service_numbers"]

        for service_number in potential_service_numbers:
            # /api/Inventory
            client_info = await self._get_client_info(client_id, service_number)
            if not client_info:
                continue

            # TODO: check where to get the first site id
            if len(client_info) > 1:
                self._logger.warning(
                    "Client Info response contains more than one element. Using just the first one."
                )
            client_info = client_info[0]
            site_id = client_info["siteID"]

            # /api/Site
            site_contact_info = self._get_site_contact_info(client_id, site_id)
            contact_info_dict = self._update_contactinfo_dict(
                contact_info_dict, site_id, site_contact_info, service_number
            )

            # TODO: check if the contact info is filled, otherwise don't created the ticket
            #  or created with other endpoint info
            ticket_contact_info = {}  # ???

        return contact_info_dict

    def _create_outage_ticket(self, client_id, service_numbers, site_contact_info):
        response = self._bruin_repository.create_outage_ticket(
            client_id, service_numbers, site_contact_info
        )
        if response["status"] not in range(200, 300):
            self._logger.error("TODO: error creating voo ticket")

        self._logger.info(
            f"VOO Ticket created for client_id {client_id} and service_number {service_number} - "
            f"{response.get('body')}"
        )

    def _create_affecting_ticket(self, client_id, service_numbers, site_contact_info):
        response = self._bruin_repository.create_affecting_ticket(
            client_id, service_numbers, site_contact_info
        )
        if response["status"] not in range(200, 300):
            self._logger.error("TODO: error creating vas ticket")

        self._logger.info(
            f"VAS Ticket created for client_id {client_id} and service_number {service_number} - "
            f"{response.get('body')}"
        )

    def _create_ticket(self, client_id, contact_info, prediction):
        site_contact_info = contact_info["site_contact_info"]
        service_numbers = contact_info["service_numbers"]

        if prediction["prediction_class"] == "VOO":
            if prediction["above_threshold"] and not prediction["in_validation_set"]:
                self._create_outage_ticket(
                    client_id, service_numbers, site_contact_info
                )

        elif prediction["prediction_class"] == "VAS":
            if prediction["above_threshold"] and not prediction["in_validation_set"]:
                self._create_affecting_ticket(
                    client_id, service_numbers, site_contact_info
                )

    async def _process_repair_email(self, email_data: dict):
        self._logger.info("Running Repair Email Process")
        # TODO: define the new logic
        email = email_data["email"]
        email_id = email["email_id"]
        client_id = email["client_id"]
        parent_id = email.get("parent_id", None)
        tag = email["tag"]

        async with self._semaphore:
            self._logger.info("Entering semaphore")
            prediction = await self._get_prediction(email_data)

            contact_info_dict = await self._get_definitive_contact_infos(
                client_id, prediction
            )

            self._logger.info(
                f"email_id: {email_id} client_id: {client_id} prediction class {prediction['prediction_class']}"
            )

            for site_id, contact_info in contact_info_dict.items():
                self._create_ticket(client_id, contact_info, prediction)

            # self._repair_tickets_kre_repository.save_predictions(
            #     client_id, site_id, service_number, site_contact_info, prediction)

            # Remove from DB
            self._repair_tickets_repository.mark_complete(email_id)
