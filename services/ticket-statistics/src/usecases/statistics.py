import pytz
import time
from datetime import datetime

from adapters.repositories.tickets.repo import TicketsRepository
from adapters.repositories.metrics.repo import MetricsRepository

utc = pytz.UTC


class StatisticsUseCase:
    def __init__(self, logger, tickets_repository: TicketsRepository, metrics_repository: MetricsRepository):
        """
        Creation of ticket use case object
        :param logger:
        :param tickets_repository:
        """
        self.tickets_repository = tickets_repository
        self.metrics_repository = metrics_repository
        self.logger = logger

    @staticmethod
    def add_tasks_created(ticket_info) -> int:
        if ticket_info['createdBy'] == 'Intelygenz Ai':
            return 1
        return 0

    @staticmethod
    def add_tasks_reopened(event) -> int:
        if event['Notes'] is not None and 'MetTel\'s IPA*#\nRe-opening ticket.' in event['Notes']:
            return 1
        return 0

    @staticmethod
    def add_device_rebooted(event) -> int:
        if event['Notes'] is not None and '#*MetTel\'s IPA*#\nOffline DiGi interface identified for serial' in \
                event['Notes']:
            return 1
        return 0

    @staticmethod
    def check_ai_resolved_task(event) -> int:
        if event['Notes'] is not None and 'MetTel\'s IPA AI is resolving the task for' in event['Notes']:
            return 1
        return 0

    @staticmethod
    def check_ai_forwarded(event) -> int:
        if event['Notes'] is not None and '#*MetTel\'s IPA*#\nDiGi reboot failed' in event['Notes']:
            return 1
        return 0

    @staticmethod
    def check_dispatch_reminders(event) -> int:
        if event['Notes'] is not None and \
                '#*MetTel\'s IPA*#' in event['Notes'] and \
                'prior reminder sent to' in event['Notes']:
            return 1
        return 0

    @staticmethod
    def check_dispatch_monitored(event) -> int:
        if event['Notes'] is not None and \
                '#*MetTel\'s IPA*#' in event['Notes'] and \
                'Dispatch Management - Dispatch Requested' in event['Notes']:
            return 1
        return 0

    @staticmethod
    def check_auto_resolved_task(event) -> bool:
        if event['Notes'] is not None and '#*MetTel\'s IPA*#\nAuto-resolving detail for serial' in event['Notes']:
            return True
        return False

    @staticmethod
    def get_resolution_date(ticket):
        fmt = '%m/%d/%Y %I:%M:%S %p'

        if 'resolveDate' in ticket:
            create_date = datetime.strptime(ticket['createDate'], fmt)
            resolve_date = datetime.strptime(ticket['resolveDate'], fmt)
            minutes_diff = (resolve_date - create_date).total_seconds() / 60.0

            return {
                'creation': ticket['createDate'],
                'resolved': ticket['resolveDate'],
                'diff': minutes_diff,
            }
        return None

    @staticmethod
    def parse_time(time):
        # Bruin is bullshit that puts : in the timezone.
        if ":" == time[-3:-2]:
            time = time[:-3] + time[-2:]
        # Bruin is even bigger bullshit that doesn't have consistency in format.
        if '.' not in time:
            note_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
        else:
            note_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z')
        return note_time

    def get_acknowledge_date(self, ticket, event):
        if event['Note Entered By']:
            format_ticket = '%m/%d/%Y %I:%M:%S %p'

            if event['EnteredDate']:
                create_date = datetime.strptime(ticket['createDate'], format_ticket).replace(tzinfo=utc)
                acknowledge_date = self.parse_time(event['EnteredDate_N'])
                minutes_diff = (acknowledge_date - create_date).total_seconds() / 60
                return {
                    'creation': ticket['createDate'],
                    'acknowledge': event['EnteredDate'],
                    'diff': minutes_diff,
                }
        return None

    @staticmethod
    def calculate_hnoc_work_queue(no_touch_resolution, ai_forwarded_tasks, all_tasks) -> int:
        try:
            return ((no_touch_resolution + ai_forwarded_tasks) / all_tasks) * 100
        except ZeroDivisionError:
            return 0

    @staticmethod
    def calculate_average_time_list(times):
        i = 0
        total = 0

        for key, diff_time in enumerate(times):
            i = i + 1
            total += diff_time['diff']

        try:
            x = total / i
        except ZeroDivisionError:
            x = 0
        return x

    @staticmethod
    def calculate_acknowledge_date_list(times):
        i = 0
        total = 0

        for key, diff_time in enumerate(times):
            if diff_time is not None:
                i = i + 1
                total += diff_time['diff']

        try:
            x = total / i
        except ZeroDivisionError:
            x = 0
        return x

    @staticmethod
    def calculate_ipa_headcount_equivalent(no_touch_resolution, days_time_frame):
        return (no_touch_resolution / days_time_frame) / 34

    def calculate_statistics(self, start: datetime, end: datetime, save: bool):
        self.logger.info(f'Calculating statistics between {start} and {end}')
        start_time = time.perf_counter()

        all_tasks = 0
        tasks_created = 0
        tasks_reopened = 0
        auto_resolved_tasks = 0
        ai_resolved_tasks = 0
        devices_rebooted = 0
        devices_monitoring = 0
        ai_forwarded_tasks = 0
        dispatch_reminders = 0
        dispatch_monitored = 0
        tasks_resolved_times = []
        tasks_average_times_to_acknowledge = []

        tickets = self.tickets_repository.get_ticket_by_date(start=start, end=end, status=True)

        for key, ticket in enumerate(tickets):
            all_tasks += 1
            tasks_created += self.add_tasks_created(ticket_info=ticket['details'])
            ticket_resolution_date = self.get_resolution_date(ticket=ticket['details'])
            average_time_to_acknowledge = False

            if ticket_resolution_date is not None:
                tasks_resolved_times.append(ticket_resolution_date)

            for event in ticket['events']:
                tasks_reopened += self.add_tasks_reopened(event=event)
                devices_rebooted += self.add_device_rebooted(event=event)
                auto_resolved_tasks += self.check_auto_resolved_task(event=event)
                ai_resolved_tasks += self.check_ai_resolved_task(event=event)
                ai_forwarded_tasks += self.check_ai_forwarded(event=event)
                dispatch_reminders += self.check_dispatch_reminders(event=event)
                dispatch_monitored += self.check_dispatch_monitored(event=event)

                if average_time_to_acknowledge is False:
                    tasks_average_times_to_acknowledge.append(
                        self.get_acknowledge_date(ticket=ticket['details'], event=event))
                    average_time_to_acknowledge = True

        average_time_to_resolve = self.calculate_average_time_list(times=tasks_resolved_times)
        average_time_to_acknowledge_calculated = self.calculate_acknowledge_date_list(
            times=tasks_average_times_to_acknowledge)
        no_touch_resolution = ai_resolved_tasks + auto_resolved_tasks
        ipa_headcount_equivalent = self.calculate_ipa_headcount_equivalent(no_touch_resolution=no_touch_resolution,
                                                                           days_time_frame=1)
        hnoc_work_queue_reduced = self.calculate_hnoc_work_queue(no_touch_resolution=no_touch_resolution,
                                                                 ai_forwarded_tasks=ai_forwarded_tasks,
                                                                 all_tasks=tasks_created + tasks_reopened)

        end_time = time.perf_counter()
        elapsed_time = round(end_time - start_time, 2)
        self.logger.info(f'Finished calculating statistics between {start} and {end} in {elapsed_time}s')

        statistics = self.metrics_repository.create_statistics_object(
            tasks_created=tasks_created,
            tasks_reopened=tasks_reopened,
            no_touch_resolution=no_touch_resolution,
            ai_resolved_tasks=ai_resolved_tasks,
            auto_resolved_tasks=auto_resolved_tasks,
            devices_monitoring=devices_monitoring,
            devices_rebooted=devices_rebooted,
            hnoc_work_queue_reduced=hnoc_work_queue_reduced,
            ai_forwarded_tasks=ai_forwarded_tasks,
            dispatch_monitored=dispatch_monitored,
            dispatch_reminders=dispatch_reminders,
            average_time_to_resolve=average_time_to_resolve,
            average_time_to_acknowledge=average_time_to_acknowledge_calculated,
            ipa_headcount_equivalent=ipa_headcount_equivalent,
        )

        if save:
            self.metrics_repository.save_statistics(statistics)
            self.logger.info(f'Saved statistics between {start} and {end} in the metrics server')

        return statistics
