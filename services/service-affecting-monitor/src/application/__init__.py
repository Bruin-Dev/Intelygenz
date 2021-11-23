import re
from enum import Enum
ALL_FIS_CLIENTS = object()


class AffectingTroubles(Enum):
    LATENCY = 'Latency'
    PACKET_LOSS = 'Packet Loss'
    JITTER = 'Jitter'
    BANDWIDTH_OVER_UTILIZATION = 'Bandwidth Over Utilization'


TROUBLES_DISJUNCTION_FOR_REGEX = '|'.join(trouble.value for trouble in AffectingTroubles)

AFFECTING_NOTE_REGEX = re.compile(
    rf"^#\*(Automation Engine|MetTel's IPA)\*#\n.*Trouble: ({TROUBLES_DISJUNCTION_FOR_REGEX})",
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
