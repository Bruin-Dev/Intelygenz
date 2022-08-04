from dataclasses import dataclass

EMAIL_STATUS = "Marked as {status} by {subject}"


@dataclass
class SentenceFormatter:
    _subject: str

    def email_marked_as(self, status: str) -> str:
        return EMAIL_STATUS.format(status=status, subject=self._subject)

    def subject(self):
        return self._subject
