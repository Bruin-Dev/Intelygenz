import time
from datetime import datetime

from adapters.repositories.tickets.repo import TicketsRepository
from dateutil.parser import isoparse


class StatisticsUseCase:
    def __init__(self, config, logger, tickets_repository: TicketsRepository):
        """
        Creation of ticket use case object
        :param logger:
        :param tickets_repository:
        """
        self.tickets_repository = tickets_repository
        self.config = config
        self.logger = logger

    def calculate_statistics(self, start: datetime, end: datetime):
        self.logger.info(f"Calculating statistics between {start} and {end}")
        start_time = time.perf_counter()

        tasks_created = 0
        tasks_reopened = 0
        devices_rebooted = 0
        ai_forwarded_tasks = 0
        ai_resolved_tasks = 0
        auto_resolved_tasks = 0
        times_to_acknowledge = []
        times_to_resolve = []

        tickets = self.tickets_repository.get_ticket_by_date(start=start, end=end, status=True)

        for ticket in tickets:
            assign_event = None

            if self.is_created_by_ipa(ticket):
                tasks_created += 1

            for event in ticket["events"]:
                if not assign_event and self.is_assigned(event):
                    assign_event = event

                if not event["Notes"] or not self.is_public_event(event) or not self.is_triggered_by_ipa(event):
                    continue

                if self.has_reopen_note(event):
                    tasks_reopened += 1

                elif self.has_device_rebooted_note(event):
                    devices_rebooted += 1

                elif self.has_ai_forwarded_note(event):
                    ai_forwarded_tasks += 1

                elif self.has_ai_resolve_note(event):
                    ai_resolved_tasks += 1
                    times_to_resolve.append(self.get_time_since_creation(event))

                elif self.has_auto_resolve_note(event):
                    auto_resolved_tasks += 1
                    times_to_resolve.append(self.get_time_since_creation(event))

            if assign_event:
                times_to_acknowledge.append(self.get_time_since_creation(assign_event))

        no_touch_resolution = ai_resolved_tasks + auto_resolved_tasks
        ipa_headcount_equivalent = self.calculate_ipa_headcount_equivalent(no_touch_resolution, start, end)
        hnoc_work_queue_reduced = self.calculate_hnoc_work_queue(
            no_touch_resolution, ai_forwarded_tasks, tasks_created, tasks_reopened
        )
        average_time_to_acknowledge = self.calculate_average(times_to_acknowledge)
        average_time_to_resolve = self.calculate_average(times_to_resolve)

        end_time = time.perf_counter()
        elapsed_time = round(end_time - start_time, 2)
        self.logger.info(f"Finished calculating statistics between {start} and {end} in {elapsed_time}s")

        return {
            "tasks_created": tasks_created,
            "tasks_reopened": tasks_reopened,
            "devices_rebooted": devices_rebooted,
            "ai_forwarded_tasks": ai_forwarded_tasks,
            "ai_resolved_tasks": ai_resolved_tasks,
            "auto_resolved_tasks": auto_resolved_tasks,
            "no_touch_resolution": no_touch_resolution,
            "ipa_headcount_equivalent": ipa_headcount_equivalent,
            "hnoc_work_queue_reduced": hnoc_work_queue_reduced,
            "average_time_to_resolve": average_time_to_resolve,
            "average_time_to_acknowledge": average_time_to_acknowledge,
        }

    @staticmethod
    def is_created_by_ipa(ticket) -> bool:
        return ticket["details"]["createdBy"] == "Intelygenz Ai"

    @staticmethod
    def is_triggered_by_ipa(event):
        return event["Note Entered By"] == "Intelygenz Ai"

    @staticmethod
    def is_public_event(event):
        return event["NoteType"] == "ADN"

    @staticmethod
    def is_assigned(event) -> bool:
        return event["Task Assigned To"] is not None

    @staticmethod
    def has_reopen_note(event) -> bool:
        return "MetTel's IPA*#\nRe-opening ticket." in event["Notes"]

    @staticmethod
    def has_device_rebooted_note(event) -> bool:
        return "#*MetTel's IPA*#\nOffline DiGi interface identified for serial" in event["Notes"]

    @staticmethod
    def has_ai_forwarded_note(event) -> bool:
        return "#*MetTel's IPA*#\nDiGi reboot failed" in event["Notes"]

    @staticmethod
    def has_ai_resolve_note(event) -> bool:
        return "MetTel's IPA AI is resolving the task for" in event["Notes"]

    @staticmethod
    def has_auto_resolve_note(event) -> bool:
        return "#*MetTel's IPA*#\nAuto-resolving detail for serial" in event["Notes"]

    @staticmethod
    def get_time_since_creation(event) -> float:
        create_date = isoparse(event["EnteredDate"])
        event_date = isoparse(event["EnteredDate_N"])
        return (event_date - create_date).total_seconds()

    @staticmethod
    def calculate_average(items) -> float:
        if not items:
            return 0
        return sum(items) / len(items)

    @staticmethod
    def calculate_hnoc_work_queue(no_touch_resolution, ai_forwarded_tasks, tasks_created, tasks_reopened) -> float:
        tasks = tasks_created + tasks_reopened
        if not tasks:
            return 0
        return ((no_touch_resolution + ai_forwarded_tasks) / tasks) * 100

    def calculate_ipa_headcount_equivalent(self, no_touch_resolution, start, end) -> float:
        seconds_in_a_day = 60 * 60 * 24
        days = (end - start).total_seconds() / seconds_in_a_day
        ipa_average_daily_tasks = no_touch_resolution / days
        return ipa_average_daily_tasks / self.config["human_average_daily_tasks"]
