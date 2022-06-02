import csv
import io
import time
from datetime import datetime, timedelta

from apscheduler.util import undefined
from pytz import timezone, utc


class DiGiRebootReport:
    def __init__(
        self, event_bus, scheduler, logger, config, bruin_repository, digi_repository, notification_repository
    ):
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._logger = logger
        self._config = config
        self._bruin_repository = bruin_repository
        self._digi_repository = digi_repository
        self._notification_repository = notification_repository

    async def start_digi_reboot_report_job(self, exec_on_start=False):
        self._logger.info(
            f"Scheduled task: DiGi reboot report process configured to run every "
            f"{self._config.DIGI_CONFIG['digi_reboot_report_time']/60} hours"
        )
        next_run_time = undefined
        if exec_on_start:
            next_run_time = datetime.now(timezone(self._config.TIMEZONE))
            self._logger.info(f"It will be executed now")
        self._scheduler.add_job(
            self._digi_reboot_report_process,
            "interval",
            minutes=self._config.DIGI_CONFIG["digi_reboot_report_time"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_digi_reboot_report",
        )

    async def _digi_reboot_report_process(self):
        self._logger.info("Starting DiGi reboot report process")
        start = time.time()

        self._logger.info("Grabbing DiGi recovery logs")

        digi_recovery_logs_response = await self._digi_repository.get_digi_recovery_logs()
        digi_recovery_logs_response_body = digi_recovery_logs_response["body"]
        digi_recovery_logs_response_status = digi_recovery_logs_response["status"]

        if digi_recovery_logs_response_status not in range(200, 300):
            return

        self._digi_recovery_logs = digi_recovery_logs_response_body["Logs"]

        ticket_id_list = self._get_all_ticket_ids_from_digi_recovery_logs()
        ticket_task_history_map = await self._get_ticket_task_histories(ticket_id_list)
        self._merge_recovery_logs(ticket_task_history_map)
        await self._generate_and_email_csv_file(ticket_task_history_map)
        stop = time.time()

        self._logger.info(f"DiGi reboot report process finished in {round((stop - start) / 60, 2)} minutes")

    def _get_all_ticket_ids_from_digi_recovery_logs(self):
        self._logger.info("Creating a list of all ticket IDS from the DiGi recovery logs")
        digi_ticket_ids = []

        for recovery_log in self._digi_recovery_logs:
            ticket_id = int(recovery_log["TicketID"])
            if ticket_id not in digi_ticket_ids:
                digi_ticket_ids.append(ticket_id)

        self._logger.info("List of all DiGi ticket IDS created")
        self._logger.info(digi_ticket_ids)
        return digi_ticket_ids

    async def _get_ticket_task_histories(self, ticket_id_list):
        ticket_map = {}
        self._logger.info("Creating ticket map of ticket id to ticket task history")
        for ticket_id in ticket_id_list:
            self._logger.info(f"Grabbing the ticket task history for ticket {ticket_id}")
            ticket_task_history_response = await self._bruin_repository.get_ticket_task_history(ticket_id)
            ticket_task_history_response_body = ticket_task_history_response["body"]
            ticket_task_history_response_status = ticket_task_history_response["status"]
            if ticket_task_history_response_status not in range(200, 300):
                continue
            self._logger.info(f"Parsing all data in the ticket task history for ticket {ticket_id}")
            ticket_info = self._parse_ticket_history(ticket_task_history_response_body)
            if ticket_info["reboot_attempted"]:
                tz = timezone(self._config.TIMEZONE)
                yesterday_timestamp = datetime.now(tz) - timedelta(days=1)
                if ticket_info["reboot_time"].date() == yesterday_timestamp.date():
                    ticket_map[ticket_id] = ticket_info

        return ticket_map

    def _parse_ticket_history(self, ticket_history):
        ticket_info = {
            "outage_type": "Unclassified",
            "reboot_attempted": False,
            "reboot_time": None,
            "process_attempted": False,
            "process_successful": False,
            "process_start": None,
            "process_end": None,
            "process_length": None,
            "reboot_method": None,
            "autoresolved": False,
            "autoresolve_time": None,
            "autoresolve_correlation": False,
            "autoresolve_diff": None,
            "forwarded": False,
        }

        for entry in ticket_history:
            if "NoteType" not in entry or entry["NoteType"] != "ADN" or entry["Notes"] is None:
                continue

            note = entry["Notes"]

            time = entry["EnteredDate_N"]
            if ":" == time[-3:-2]:
                time = time[:-3] + time[-2:]

            if "." not in time:
                note_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")
            else:
                note_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f%z")

            if "Triage" in entry["Notes"]:
                edge_status = self._get_edge_status_from_note(note)

                if edge_status:
                    if edge_status == "CONNECTED":
                        ticket_info["outage_type"] = "Link"
                    else:
                        ticket_info["outage_type"] = "Edge"

            if "Offline DiGi interface identified" in note:
                ticket_info["reboot_attempted"] = True
                ticket_info["reboot_time"] = note_time

            if "DiGi reboot failed" in note:
                ticket_info["forwarded"] = True

            if "Auto-resolving detail for serial" in note:
                ticket_info["autoresolve_time"] = note_time

        return ticket_info

    def _get_edge_status_from_note(self, text):
        if "Edge Status" in text:
            index = text.index("Edge Status: ") + 13
            status = ""
            while index < len(text):
                char = text[index]
                if char == "\n":
                    break
                status += char
                index += 1
            return status
        return None

    def _merge_recovery_logs(self, ticket_map):
        self._logger.info("Merging recovery logs data into ticket map")
        for process in self._digi_recovery_logs:
            ticket_id = int(process["TicketID"])
            if ticket_id not in ticket_map:
                continue

            self._logger.info(
                f"Merging data from DiGi recovery logs of ticket id {ticket_id} "
                f"into the ticket ID to ticket task history map"
            )
            ticket_map[ticket_id]["process_attempted"] = True
            ticket_map[ticket_id]["process_start"] = (
                datetime.strptime(process["TimestampSTART"], "%Y-%m-%dT%H:%M:%SZ")
                if process.get("TimestampSTART") is not None
                else None
            )
            ticket_map[ticket_id]["process_end"] = (
                datetime.strptime(process["TimestampEND"], "%Y-%m-%dT%H:%M:%SZ")
                if process.get("TimestampEND") is not None
                else None
            )

            if process.get("Success"):
                ticket_map[ticket_id]["process_successful"] = True

            autoresolve_time = ticket_map[ticket_id]["autoresolve_time"]

            if ticket_map[ticket_id]["process_end"] is not None:
                utc_time = utc.localize(ticket_map[ticket_id]["process_end"])
                tz = timezone(self._config.TIMEZONE)
                etc_converted_end_time = utc_time.astimezone(tz)

                ticket_map[ticket_id]["process_length"] = (
                    (ticket_map[ticket_id]["process_end"] - ticket_map[ticket_id]["process_start"]).total_seconds() / 60
                    if ticket_map[ticket_id]["process_start"]
                    else None
                )
                if autoresolve_time:
                    if etc_converted_end_time <= autoresolve_time < (autoresolve_time + timedelta(minutes=10)):
                        ticket_map[ticket_id]["autoresolved"] = True
                    autoresolve_diff = (autoresolve_time - etc_converted_end_time).total_seconds() / 60
                    ticket_map[ticket_id]["autoresolve_diff"] = autoresolve_diff
                    ticket_map[ticket_id]["autoresolve_correlation"] = -10 < autoresolve_diff < 30
            ticket_map[ticket_id]["reboot_method"] = process["Method"]

    def _track_process_length(self, day, process_length, process_length_by_day):

        if not process_length:
            return

        if day not in process_length_by_day:
            process_length_by_day[day] = {"count": 0, "total": 0}

        process_length_by_day[day]["count"] += 1
        process_length_by_day[day]["total"] += process_length

    def _merge_process_length_avg(self, breakdown, process_length_by_day):

        for day in process_length_by_day:
            breakdown[day][8] = round(
                process_length_by_day[day]["total"] / (process_length_by_day[day]["count"] * 1.0), 2
            )

    async def _generate_and_email_csv_file(self, ticket_map):
        self._logger.info("Generating a csv file from the ticket map of ticket IDs to ticket task histories")
        fields = [
            "Time (EST)",  # 0
            "Reboot Request Attempts",  # 1
            "Edge Outages",  # 2
            "Link Outages",  # 3
            "Unclassified Outages",  # 4
            "Reboot Request Successful",  # 5
            "DiGi Reboot Process Attempts",  # 6
            "DiGi Reboot Process Successful",  # 7
            "Average DiGi Reboot Process Length",  # 8
            "Ping Reboots Attempted",  # 9
            "Ping Reboots Successful",  # 10
            "OEMPortal Reboots Attempted",  # 11
            "OEMPortal Reboots Successful",  # 12
            "SSH Reboots Attempted",  # 13
            "SSH Reboots Successful",  # 14
            "SMS Reboots Attempted",  # 15
            "SMS Reboots Successful",  # 16
            "API Start Reboots Attempted",  # 17
            "API Start Reboots Successful",  # 18
            "Tasks Autoresolved within (-10,30) min",  # 19
            "Tasks Autoresolved within (-10,0] min",  # 20
            "Tasks Autoresolved within (0,10] min",  # 21
            "Tasks Autoresolved within (10,20] min",  # 22
            "Tasks Autoresolved within (20,30) min",  # 23
            "Edge Outage Tasks Autoresolved",  # 24
            "Link Outage Tasks Autoresolved",  # 25
            "Unclassified Outage Tasks Autoresolved",  # 26
            "Tasks Forwarded to Wireless",  # 27
            "Edge Outage Tasks Forwarded",  # 28
            "Link Outage Tasks Forwarded",  # 29
            "Unclassified Outage Tasks Forwarded",
        ]  # 30

        breakdown = {}
        process_length_by_day = {}
        for ticket_id in ticket_map:
            ticket_info = ticket_map[ticket_id]

            day = ticket_info["reboot_time"].strftime("%m/%d")

            if day not in breakdown:
                breakdown[day] = [day] + ([0] * (len(fields) - 1))

            breakdown[day][1] += 1

            outage_type = ticket_info["outage_type"]

            if outage_type == "Edge":
                breakdown[day][2] += 1
            if outage_type == "Link":
                breakdown[day][3] += 1
            if outage_type == "Unclassified":
                breakdown[day][4] += 1

            breakdown[day][5] += 1

            if ticket_info["process_attempted"]:
                breakdown[day][6] += 1

            methods = {
                "Ping": 9,
                "OEMPortal": 11,
                "SSH": 13,
                "SMS": 15,
                "API Start": 17,
            }

            method = ticket_info["reboot_method"]

            if method is not None:
                breakdown[day][methods[method]] += 1

            process_successful = ticket_info["process_successful"]

            if process_successful:
                breakdown[day][7] += 1
                if method is not None:
                    breakdown[day][methods[method] + 1] += 1
                self._track_process_length(day, ticket_info["process_length"], process_length_by_day)

            if ticket_info["autoresolve_correlation"] and method in ["OEMPortal", "SSH", "SMS"]:
                breakdown[day][19] += 1

                autoresolve_diff = ticket_info["autoresolve_diff"]
                if -10 < autoresolve_diff <= 0:
                    breakdown[day][20] += 1
                if 0 < autoresolve_diff <= 10:
                    breakdown[day][21] += 1
                if 10 < autoresolve_diff <= 20:
                    breakdown[day][22] += 1
                if 20 < autoresolve_diff < 30:
                    breakdown[day][23] += 1

                if outage_type == "Edge":
                    breakdown[day][24] += 1
                if outage_type == "Link":
                    breakdown[day][25] += 1
                if outage_type == "Unclassified":
                    breakdown[day][26] += 1

            if ticket_info["forwarded"]:
                breakdown[day][27] += 1

                if outage_type == "Edge":
                    breakdown[day][28] += 1
                if outage_type == "Link":
                    breakdown[day][29] += 1
                if outage_type is "Unclassified":
                    breakdown[day][30] += 1
        self._merge_process_length_avg(breakdown, process_length_by_day)

        days = list(breakdown.keys())
        days.sort()

        filename = "digi_recovery_report.csv"

        with open(filename, "w"):
            buf = io.StringIO()
            csvwriter = csv.writer(buf)
            csvwriter.writerow(fields)
            for day in days:
                csvwriter.writerow(breakdown[day])
            buf.seek(0)
            raw_csv = buf.read()
            self._logger.info("Sending csv file through email")
            await self._notification_repository.send_email(raw_csv)
