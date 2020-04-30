import os

from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

from dateutil.parser import parse

from application.repositories.ticket_repository import TicketRepository
from application.repositories.utils_repository import UtilsRepository
from application.repositories import ticket_repository as ticket_repository_module
from config import testconfig


class TestTicketRepository:
    def is_detail_resolved_test(self):
        ticket_detail = {
            "detailID": 12345,
            "detailValue": 'VC1234567',
            "detailStatus": "I",
        }
        result = TicketRepository.is_detail_resolved(ticket_detail)
        assert result is False

        ticket_detail = {
            "detailID": 12345,
            "detailValue": 'VC1234567',
            "detailStatus": "R",
        }
        result = TicketRepository.is_detail_resolved(ticket_detail)
        assert result is True

    def is_tnba_note_test(self):
        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        result = TicketRepository.is_tnba_note(ticket_note)
        assert result is False

        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        result = TicketRepository.is_tnba_note(ticket_note)
        assert result is False

        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nAuto-resolving ticket.\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        result = TicketRepository.is_tnba_note(ticket_note)
        assert result is False

        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nRe-opening ticket.\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        result = TicketRepository.is_tnba_note(ticket_note)
        assert result is False

        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": '2019-12-30T06:38:13.503-05:00',
        }
        result = TicketRepository.is_tnba_note(ticket_note)
        assert result is True

    def find_newest_tnba_note_test(self):
        ticket_note_1 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T10:07:13.503-05:00",
        }
        ticket_note_2 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T12:07:13.503-05:00",
        }
        ticket_note_3 = {
            "noteId": 41894040,
            "noteValue": f'#*Automation Engine*#\nTNBA\nTimeStamp: 2019-07-30 06:38:00+00:00',
            "createdDate": "2020-02-24T11:07:13.503-05:00",
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
        ]

        utils_repository = UtilsRepository()
        config = testconfig

        ticket_repository = TicketRepository(config, utils_repository)

        result = ticket_repository.find_newest_tnba_note(ticket_notes)

        assert result == ticket_note_3

    def is_note_older_than_test(self):
        ticket_note_creation_date: str = '2019-12-30T06:38:13.503-05:00'
        ticket_note_creation_datetime = parse(ticket_note_creation_date)
        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": ticket_note_creation_date,
        }

        now = ticket_note_creation_datetime + timedelta(minutes=5)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=now)

        with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
            note_age = timedelta(minutes=4)
            result = TicketRepository.is_note_older_than(ticket_note, age=note_age)
            assert result is True

            note_age = timedelta(minutes=5)
            result = TicketRepository.is_note_older_than(ticket_note, age=note_age)
            assert result is True

            note_age = timedelta(minutes=6)
            result = TicketRepository.is_note_older_than(ticket_note, age=note_age)
            assert result is False

    def is_tnba_note_old_enough_test(self):
        ticket_note_creation_date: str = '2019-12-30T06:38:13.503-05:00'
        ticket_note_creation_datetime = parse(ticket_note_creation_date)
        ticket_note = {
            "noteId": 41894043,
            "noteValue": f'#*Automation Engine*#\nTimeStamp: 2019-12-30T06:38:13.503-05:00',
            "createdDate": ticket_note_creation_date,
        }

        utils_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['tnba_notes_age_for_new_appends_in_minutes'] = 30

        ticket_repository = TicketRepository(config, utils_repository)

        datetime_mock = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            now = ticket_note_creation_datetime + timedelta(minutes=31)
            datetime_mock.now = Mock(return_value=now)
            with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
                result = ticket_repository.is_tnba_note_old_enough(ticket_note)
                assert result is True

            now = ticket_note_creation_datetime + timedelta(minutes=30)
            datetime_mock.now = Mock(return_value=now)
            with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
                result = ticket_repository.is_tnba_note_old_enough(ticket_note)
                assert result is True

            now = ticket_note_creation_datetime + timedelta(minutes=29)
            datetime_mock.now = Mock(return_value=now)
            with patch.object(ticket_repository_module, 'datetime', new=datetime_mock):
                result = ticket_repository.is_tnba_note_old_enough(ticket_note)
                assert result is False

    def build_tnba_note_from_predictions_test(self):
        predictions = [
            {
                'name': 'Repair Completed',
                'probability': 0.9484384655952454
            },
            {
                'name': 'Holmdel NOC Investigate',
                'probability': 0.1234567890123456
            },
        ]

        result = TicketRepository.build_tnba_note_from_predictions(predictions)

        assert result == os.linesep.join([
            '#*Automation Engine*#',
            'TNBA',
            '',
            'The following are the next best actions for this ticket with corresponding confidence levels:',
            '1) Repair Completed | Confidence: 94.84384655952454 %',
            '2) Holmdel NOC Investigate | Confidence: 12.34567890123456 %',
        ])
