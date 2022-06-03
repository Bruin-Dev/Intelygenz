import re
from enum import Enum


class AffectingTroubles(Enum):
    LATENCY = 'Latency'
    PACKET_LOSS = 'Packet Loss'
    JITTER = 'Jitter'
    BANDWIDTH_OVER_UTILIZATION = 'Bandwidth Over Utilization'
    BOUNCING = 'Circuit Instability'


class ForwardQueues(Enum):
    ASR = 'ASR Investigate'
    HNOC = 'HNOC Investigate'


TROUBLES_DISJUNCTION_FOR_REGEX = '|'.join(trouble.value for trouble in AffectingTroubles)

AFFECTING_NOTE_REGEX = re.compile(
    rf"^#\*(Automation Engine|MetTel's IPA)\*#\n.*Trouble: (?P<trouble>{TROUBLES_DISJUNCTION_FOR_REGEX})",
    re.DOTALL | re.MULTILINE,
)
REOPEN_NOTE_REGEX = re.compile(
    rf"^#\*(Automation Engine|MetTel's IPA)\*#\n.*Re-opening ticket.*Trouble: ({TROUBLES_DISJUNCTION_FOR_REGEX})",
    re.DOTALL,
)
AUTORESOLVE_NOTE_REGEX = re.compile(
    r"^#\*(Automation Engine|MetTel's IPA)\*#\n.*Auto-resolving task for serial",
    re.DOTALL,
)

NOTE_REGEX_BY_TROUBLE = {
    trouble: re.compile(
        rf"^#\*(Automation Engine|MetTel's IPA)\*#\n.*Trouble: {trouble.value}",
        re.DOTALL | re.MULTILINE
    )
    for trouble in AffectingTroubles
}

LINK_INFO_REGEX = re.compile(
    rf'Edge Name: (?P<edge_name>.+)\n'
    rf'Name: (?P<label>.+)\n'
    rf'Interface: (?P<interface>.+)\n'
    rf'IP Address: (?P<ip>.+)\n'
    rf'Link Type: (Unknown|(?P<mode>Public|Private) (?P<type>Wired|Wireless))\n'
)

EVENT_INTERFACE_REGEX = re.compile(
    r'(^Interface (?P<interface>[a-zA-Z0-9]+) is (up|down)$)|'
    r'(^Link (?P<link_interface>[a-zA-Z0-9]+) is (no longer|now) DEAD$)'
)

REMINDER_NOTE_REGEX = re.compile(
    r"^#\*MetTel's IPA\*#\nClient Reminder",
    re.DOTALL | re.MULTILINE,
)
