import re
from enum import Enum, auto


class Outages(Enum):
    LINK_DOWN = "Link Down (no HA)"
    HARD_DOWN = "Hard Down (no HA)"

    HA_LINK_DOWN = "Link Down (HA)"
    HA_SOFT_DOWN = "Soft Down (HA)"
    HA_HARD_DOWN = "Hard Down (HA)"


class ForwardQueues(Enum):
    ASR = "ASR Investigate"
    HNOC = "HNOC Investigate"
    WIRELESS = "Wireless Repair Intervention Needed"


class ChangeTicketSeverityStatus(Enum):
    CHANGED_TO_LINK_DOWN_SEVERITY = auto()
    CHANGED_TO_EDGE_DOWN_SEVERITY = auto()
    NOT_CHANGED = auto()


TRIAGE_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nTriage \(VeloCloud\)")
REOPEN_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nRe-opening")
AUTORESOLVE_NOTE_REGEX = re.compile(r"^#\*(Automation Engine|MetTel's IPA)\*#\nAuto-resolving detail for serial")
DIGI_NOTE_REGEX = re.compile(r"^#\*MetTel's IPA\*#\nOffline DiGi interface .*\nInterface: (?P<interface>\w+)")
REMINDER_NOTE_REGEX = re.compile(r"^#\*MetTel's IPA\*#\nClient Reminder")

OUTAGES_DISJUNCTION_FOR_REGEX = "|".join(re.escape(outage_type.value) for outage_type in Outages)
OUTAGE_TYPE_REGEX = re.compile(rf"Outage Type: (?P<outage_type>{OUTAGES_DISJUNCTION_FOR_REGEX})")

LINK_INFO_REGEX = re.compile(
    rf"Interface (?P<interface>\w+)\n"
    rf"Interface \w+ Label: (?P<label>.+)\n"
    rf"Interface \w+ IP Address: (?P<ip>.+)\n"
    rf"Interface \w+ Type: (Unknown|(?P<mode>Public|Private) (?P<type>Wired|Wireless))\n"
    rf"Interface \w+ Status: (?P<status>.+)\n"
)

EVENT_INTERFACE_NAME_REGEX = re.compile(
    r"(^Interface (?P<interface_name>[a-zA-Z0-9]+) is (up|down)$)|"
    r"(^Link (?P<interface_name2>[a-zA-Z0-9]+) is (no longer|now) DEAD$)"
)

FORWARD_TICKET_TO_HNOC_JOB_ID = "_forward_ticket_{ticket_id}_{serial_number}_to_hnoc"
