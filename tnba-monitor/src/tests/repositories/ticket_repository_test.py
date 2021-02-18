import os

from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

from dateutil.parser import parse

from application.repositories.ticket_repository import TicketRepository
from application.repositories import ticket_repository as ticket_repository_module


class TestTicketRepository:
    def is_detail_resolved_test(self, serial_number_1, make_resolved_ticket_detail, make_in_progress_ticket_detail):
        ticket_detail = make_in_progress_ticket_detail(serial_number=serial_number_1)
        result = TicketRepository.is_detail_resolved(ticket_detail)
        assert result is False

        ticket_detail = make_resolved_ticket_detail(serial_number=serial_number_1)
        result = TicketRepository.is_detail_resolved(ticket_detail)
        assert result is True

    def is_tnba_note_test(self, serial_number_1, make_standard_tnba_note, make_request_completed_tnba_note,
                          make_repair_completed_tnba_note, make_reopen_note, make_triage_note):
        reopen_note = make_reopen_note(serial_number=serial_number_1)
        result = TicketRepository.is_tnba_note(reopen_note)
        assert result is False

        triage_note = make_triage_note(serial_number=serial_number_1)
        result = TicketRepository.is_tnba_note(triage_note)
        assert result is False

        tnba_note = make_standard_tnba_note(serial_number=serial_number_1)
        result = TicketRepository.is_tnba_note(tnba_note)
        assert result is True

        tnba_request_completed_note = make_request_completed_tnba_note(serial_number=serial_number_1)
        result = TicketRepository.is_tnba_note(tnba_request_completed_note)
        assert result is True

        tnba_repair_completed_note = make_repair_completed_tnba_note(serial_number=serial_number_1)
        result = TicketRepository.is_tnba_note(tnba_repair_completed_note)
        assert result is True

    def has_tnba_note_test(self, ticket_repository, serial_number_1, make_standard_tnba_note, make_triage_note,
                           make_reopen_note):
        reopen_note = make_reopen_note(serial_number=serial_number_1)
        triage_note = make_triage_note(serial_number=serial_number_1)
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1)

        ticket_notes = []
        result = ticket_repository.has_tnba_note(ticket_notes)
        assert result is False

        ticket_notes = [
            reopen_note,
            triage_note,
        ]
        result = ticket_repository.has_tnba_note(ticket_notes)
        assert result is False

        ticket_notes = [
            tnba_note,
            reopen_note,
            triage_note,
        ]
        result = ticket_repository.has_tnba_note(ticket_notes)
        assert result is True

    def find_newest_tnba_note_by_service_number_test(self, ticket_repository, serial_number_1, make_standard_tnba_note):
        tnba_note_1 = make_standard_tnba_note(serial_number=serial_number_1, date='2020-02-24T11:07:13.503-05:00')
        tnba_note_2 = make_standard_tnba_note(serial_number=serial_number_1, date='2020-02-25T11:07:13.503-05:00')
        tnba_note_3 = make_standard_tnba_note(serial_number=serial_number_1, date='2020-02-26T11:07:13.503-05:00')

        ticket_notes = [
            tnba_note_1,
            tnba_note_2,
            tnba_note_3,
        ]
        result = ticket_repository.find_newest_tnba_note_by_service_number(ticket_notes, serial_number_1)
        assert result is tnba_note_3

    def is_note_older_than_test(self, serial_number_1, make_standard_tnba_note):
        ticket_note_creation_date: str = '2019-12-30T06:38:13.503-05:00'
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1, date=ticket_note_creation_date)

        ticket_note_creation_datetime = parse(ticket_note_creation_date)
        now = ticket_note_creation_datetime + timedelta(minutes=5)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=now)

        with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
            note_age = timedelta(minutes=4)
            result = TicketRepository.is_note_older_than(tnba_note, age=note_age)
            assert result is True

            note_age = timedelta(minutes=5)
            result = TicketRepository.is_note_older_than(tnba_note, age=note_age)
            assert result is True

            note_age = timedelta(minutes=6)
            result = TicketRepository.is_note_older_than(tnba_note, age=note_age)
            assert result is False

    def is_tnba_note_old_enough_test(self, ticket_repository, serial_number_1, make_standard_tnba_note):
        ticket_note_creation_date: str = '2019-12-30T06:38:13.503-05:00'
        tnba_note = make_standard_tnba_note(serial_number=serial_number_1, date=ticket_note_creation_date)

        ticket_note_creation_datetime = parse(ticket_note_creation_date)
        datetime_mock = Mock()

        now = ticket_note_creation_datetime + timedelta(minutes=31)
        datetime_mock.now = Mock(return_value=now)
        with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
            result = ticket_repository.is_tnba_note_old_enough(tnba_note)
            assert result is True

        now = ticket_note_creation_datetime + timedelta(minutes=30)
        datetime_mock.now = Mock(return_value=now)
        with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
            result = ticket_repository.is_tnba_note_old_enough(tnba_note)
            assert result is True

        now = ticket_note_creation_datetime + timedelta(minutes=29)
        datetime_mock.now = Mock(return_value=now)
        with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
            result = ticket_repository.is_tnba_note_old_enough(tnba_note)
            assert result is False

    def is_detail_in_outage_ticket_test(self, make_detail_object):
        detail_object = make_detail_object(ticket_topic='Service Outage Trouble')
        result = TicketRepository.is_detail_in_outage_ticket(detail_object)
        assert result is True

        detail_object = make_detail_object(ticket_topic='Service Affecting Trouble')
        result = TicketRepository.is_detail_in_outage_ticket(detail_object)
        assert result is False

    def was_ticket_created_by_automation_engine_test(self, make_detail_object):
        detail_object = make_detail_object(ticket_creator='Intelygenz Ai')
        result = TicketRepository.was_ticket_created_by_automation_engine(detail_object)
        assert result is True

        detail_object = make_detail_object(ticket_creator='Otacon')
        result = TicketRepository.was_ticket_created_by_automation_engine(detail_object)
        assert result is False

    def build_tnba_note_from_prediction_test(self, serial_number_1, holmdel_noc_prediction):
        result = TicketRepository.build_tnba_note_from_prediction(holmdel_noc_prediction, serial_number_1)

        assert result == os.linesep.join([
            "#*MetTel's IPA*#",
            'TNBA',
            '',
            'The next best action for VC1234567 is: Holmdel NOC Investigate.',
            '',
            'TNBA is based on AI model designed specifically for MetTel.',
        ])

    def build_tnba_note_from_request_or_repair_completed_prediction_test(self, serial_number_1,
                                                                         confident_repair_completed_prediction):
        result = TicketRepository.build_tnba_note_from_request_or_repair_completed_prediction(
            confident_repair_completed_prediction, serial_number_1
        )

        assert result == os.linesep.join([
            "#*MetTel's IPA*#",
            'TNBA',
            '',
            'The next best action for VC1234567 is: Repair Completed. Since it is a high confidence prediction',
            'the task has been automatically transitioned.',
            '',
            'TNBA is based on AI model designed specifically for MetTel.',
        ])
