import re
from enum import Enum


class ForwardQueues(Enum):
    HNOC = "HNOC Investigate"
    IPA = "IPA Investigate"


US_STATES_PATTERN = re.compile(
    r"(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|"
    r"PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)"
).pattern
ZIP_CODE_REGEX = re.compile(rf"{US_STATES_PATTERN},? (?P<zip_code>\d{{5}})")

TRIAGE_NOTE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nInterMapper Triage")
REOPEN_NOTE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nRe-opening")
EVENT_REGEX = re.compile(r"Event:\s*(?P<event>\w+)")
EVENT_TIME_REGEX = re.compile(r"(?P<time>^.*): Message from InterMapper (?P<version>.*)")
CONDITION_REGEX = re.compile("^CONDITION: (?P<condition>.*)", re.MULTILINE)
AUTORESOLVE_REGEX = re.compile(r"^#\*(MetTel's IPA)\*#\nAuto-resolving task for")
