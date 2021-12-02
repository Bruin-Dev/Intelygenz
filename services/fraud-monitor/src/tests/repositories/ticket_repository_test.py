from datetime import datetime, timedelta


class TestTicketRepository:
    def instance_test(self, ticket_repository, utils_repository):
        assert ticket_repository._utils_repository is utils_repository

    def is_task_resolved_test(self, ticket_repository, make_detail_item):
        detail_item = make_detail_item(status='I')
        result = ticket_repository.is_task_resolved(detail_item)
        assert result is False

        detail_item = make_detail_item(status='R')
        result = ticket_repository.is_task_resolved(detail_item)
        assert result is True

    def is_fraud_ticket_test(self, ticket_repository, make_ticket_note):
        result = ticket_repository.is_fraud_ticket([])
        assert result is True

        note = make_ticket_note(text=f"#*MetTel's IPA*#\nPossible Fraud Warning")
        result = ticket_repository.is_fraud_ticket([note])
        assert result is True

        note = make_ticket_note(text='Dummy note')
        result = ticket_repository.is_fraud_ticket([note])
        assert result is False

    def find_task_test(self, ticket_repository, make_detail_item):
        serial_number = 'VC1234567'

        detail_item = make_detail_item(value='VC0000000')
        result = ticket_repository.find_task([detail_item], serial_number)
        assert result is None

        detail_item = make_detail_item(value=serial_number)
        result = ticket_repository.find_task([detail_item], serial_number)
        assert result is detail_item

    def get_latest_notes_test(self, ticket_repository, make_ticket_note):
        current_datetime = datetime.now()

        fraud_note_1 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nPossible Fraud Warning",
            creation_date=str(current_datetime - timedelta(seconds=30)),
        )
        fraud_note_2 = make_ticket_note(
            text=f"#*MetTel's IPA*#\nPossible Fraud Warning",
            creation_date=str(current_datetime - timedelta(seconds=20)),
        )
        reopen_note = make_ticket_note(
            text=f"#*MetTel's IPA*#\nRe-opening ticket.",
            creation_date=str(current_datetime - timedelta(seconds=10)),
        )

        notes = [fraud_note_1, fraud_note_2]
        result = ticket_repository.get_latest_notes(notes)
        assert result == notes

        notes = [fraud_note_1, reopen_note]
        result = ticket_repository.get_latest_notes(notes)
        assert result == [reopen_note]

        notes = [fraud_note_1, reopen_note, fraud_note_2]
        result = ticket_repository.get_latest_notes(notes)
        assert result == [reopen_note, fraud_note_2]

    def note_already_exists_test(self, ticket_repository, make_ticket_note):
        msg_uid = '123456'
        note_1 = make_ticket_note(text='Dummy note')
        note_2 = make_ticket_note(text=f"#*MetTel's IPA*#\nPossible Fraud Warning\nEmail UID: 654321")
        note_3 = make_ticket_note(text=f"#*MetTel's IPA*#\nPossible Fraud Warning\nEmail UID: 123456")

        result = ticket_repository.note_already_exists([note_1], msg_uid)
        assert result is False

        result = ticket_repository.note_already_exists([note_2], msg_uid)
        assert result is False

        result = ticket_repository.note_already_exists([note_3], msg_uid)
        assert result is True
