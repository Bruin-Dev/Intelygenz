from asynctest import CoroutineMock
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from application.actions.repair_tickets_monitor import RepairTicketsMonitor
from application.exceptions import ResponseException
from config import testconfig as config


@pytest.fixture(scope="module")
def inference_data_voo_validation_set(make_inference_data, make_filter_flags):
    return make_inference_data(
        predicted_class='VOO',
        potential_service_numbers=["12345"],
        filter_flags=make_filter_flags(
            in_validation_set=True
        )
    )


@pytest.fixture(scope="module")
def email_data_full_details(make_email):
    return make_email(
        email_id="12345",
        client_id="30000",
        received_date=datetime.utcnow(),
        subject="test subject",
        body="test body serial number: 56789",
        from_address="test@test.com",
        to_address=["address_1@test.com", "address_2@test.com"],
        send_cc=["test_cc@test.com", "test_cc2@test.com"]
    )


@pytest.fixture(scope="module")
def existing_ticket_data_voo_with_service_numbers(make_ticket_decamelized):
    ticket = make_ticket_decamelized(
        ticket_id=1234,
        client_id="30000",
        ticket_status="In Progress",
        call_type="",
        category="VOO",
        create_date=datetime.utcnow(),
        created_by="test bot",
    )
    ticket['service_numbers'] = ["1235", "4366"]
    ticket['site_id'] = "site_name"
    return ticket


@pytest.fixture(scope="module")
def email_data_no_cc_details(make_email):
    return make_email(
        email_id="12345",
        client_id="30000",
        received_date=datetime.utcnow(),
        subject="test subject",
        body="test body serial number: 56789",
        from_address="test@test.com",
        to_address=["address_1@test.com", "address_2@test.com"],
    )


@pytest.fixture(scope="module")
def tag_data_repair():
    return {
        'tag_id': 1,
        'email_id': '12345',
    }


@pytest.fixture(scope="module")
def tag_data_new_order():
    return {
        'tag_id': 2,
        'email_id': '12345',
    }


class TestRepairTicketsMonitor:
    def instance_test(
            self,
            event_bus,
            logger,
            scheduler,
            bruin_repository,
            new_tagged_emails_repository,
            repair_ticket_kre_repository,
    ):
        repair_tickets_monitor = RepairTicketsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            bruin_repository,
            new_tagged_emails_repository,
            repair_ticket_kre_repository,
        )

        assert repair_tickets_monitor._event_bus == event_bus
        assert repair_tickets_monitor._logger == logger
        assert repair_tickets_monitor._scheduler == scheduler
        assert repair_tickets_monitor._config == config
        assert repair_tickets_monitor._bruin_repository == bruin_repository
        assert repair_tickets_monitor._new_tagged_emails_repository == new_tagged_emails_repository
        assert repair_tickets_monitor._repair_tickets_kre_repository == repair_ticket_kre_repository

    @pytest.mark.asyncio
    async def start_repair_tickets_monitor__exec_on_start_test(self, repair_tickets_monitor, scheduler):
        next_run_time = datetime.now()

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch('application.actions.repair_tickets_monitor.datetime', datetime_mock):
            await repair_tickets_monitor.start_repair_tickets_monitor(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            repair_tickets_monitor._run_repair_tickets_polling,
            'interval',
            seconds=config.MONITOR_CONFIG['scheduler_config']['repair_ticket_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_run_repair_tickets_polling'
        )

    def _triage_emails_by_tag_test(self, repair_tickets_monitor):
        tagged_emails = [{'email_id': 1234, 'tag_id': 1}, {'email_id': 1234, 'tag_id': 2}]

        repair_emails, other_emails = repair_tickets_monitor._triage_emails_by_tag(tagged_emails)

        assert list(repair_emails)[0] == tagged_emails[0]
        assert list(other_emails)[0] == tagged_emails[1]

    @pytest.mark.asyncio
    async def _get_inference__ok_test(
            self,
            repair_tickets_monitor,
            inference_data_voo_validation_set,
            make_rpc_response,
            email_data_full_details,
            tag_data_repair,
    ):
        email_data = email_data_full_details['email']
        expected_cc = ', '.join(email_data['send_cc'])
        tag_info = tag_data_repair
        rpc_response = make_rpc_response(status=200, body=inference_data_voo_validation_set)

        repair_tickets_kre_repository = CoroutineMock()
        repair_tickets_kre_repository.get_email_inference = CoroutineMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email_data, tag_info)

        repair_tickets_kre_repository.get_email_inference.assert_awaited_once(
            {
                "email_id": email_data['email_id'],
                "client_id": email_data['client_id'],
                "subject": email_data['subject'],
                "body": email_data['body'],
                "date": email_data['date'],
                "from_address": email_data['from_address'],
                "to": email_data['to_address'][0],
                "cc": expected_cc,
            },
            tag_info
        )

        assert response == inference_data_voo_validation_set

    @pytest.mark.asyncio
    async def _get_inference__no_cc_test(
            self,
            repair_tickets_monitor,
            inference_data_voo_validation_set,
            make_rpc_response,
            email_data_full_details,
            tag_data_repair,
    ):
        email_data = email_data_full_details['email']
        expected_cc = ''
        tag_info = tag_data_repair
        rpc_response = make_rpc_response(status=200, body=inference_data_voo_validation_set)

        repair_tickets_kre_repository = CoroutineMock()
        repair_tickets_kre_repository.get_email_inference = CoroutineMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email_data, tag_info)

        repair_tickets_kre_repository.get_email_inference.assert_awaited_once(
            {
                "email_id": email_data['email_id'],
                "client_id": email_data['client_id'],
                "subject": email_data['subject'],
                "body": email_data['body'],
                "date": email_data['date'],
                "from_address": email_data['from_address'],
                "to": email_data['to_address'][0],
                "cc": expected_cc,
            },
            tag_info
        )

        assert response == inference_data_voo_validation_set

    @pytest.mark.asyncio
    async def _get_inference__not_2XX_test(
            self,
            repair_tickets_monitor,
            make_rpc_response,
            email_data_full_details,
            tag_data_repair
    ):
        email_data = email_data_full_details['email']
        tag_info = tag_data_repair

        rpc_response = make_rpc_response(status=400, body='Error in data')
        repair_tickets_kre_repository = CoroutineMock()
        repair_tickets_kre_repository.get_email_inference = CoroutineMock(return_value=rpc_response)
        repair_tickets_monitor._repair_tickets_kre_repository = repair_tickets_kre_repository

        response = await repair_tickets_monitor._get_inference(email_data, tag_info)

        assert response is None

    @pytest.mark.asyncio
    async def _save_outputs__ok_test(self, repair_tickets_monitor, make_rpc_response, make_rta_ticket_payload):
        email_id = "1234"
        service_number_site_map = {"1234": "5678"}
        tickets_created = [make_rta_ticket_payload(ticket_id="5678", site_id="5678")]
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        tickets_cannot_be_created = []
        rpc_body = {"success": True}
        rpc_response = make_rpc_response(status=200, body=rpc_body)

        repair_tickets_monitor._repair_tickets_kre_repository.save_outputs = CoroutineMock(return_value=rpc_response)

        result = await repair_tickets_monitor._save_output(
            email_id,
            service_number_site_map,
            tickets_created,
            tickets_updated,
            tickets_could_be_created,
            tickets_could_be_updated,
            tickets_cannot_be_created,
        )

        assert result == rpc_body

    @pytest.mark.asyncio
    async def _save_outputs__not_2XX_test(self, repair_tickets_monitor, make_rpc_response):
        email_id = "1234"
        service_number_site_map = {"1234": "5678"}
        tickets_created = []
        tickets_updated = []
        tickets_could_be_created = []
        tickets_could_be_updated = []
        tickets_cannot_be_created = []
        rpc_body = {"Error"}
        rpc_response = make_rpc_response(status=400, body=rpc_body)

        repair_tickets_monitor._repair_tickets_kre_repository.save_outputs = CoroutineMock(return_value=rpc_response)

        result = await repair_tickets_monitor._save_output(
            email_id,
            service_number_site_map,
            tickets_created,
            tickets_updated,
            tickets_could_be_created,
            tickets_could_be_updated,
            tickets_cannot_be_created,
        )

        assert result is None

    @pytest.mark.asyncio
    async def _process_other_tags_email_test(
            self,
            repair_tickets_monitor,
            tag_data_new_order
    ):
        email_tag_data = tag_data_new_order

        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository

        await repair_tickets_monitor._process_other_tags_email(email_tag_data)

        new_tagged_emails_repository.mark_complete.assert_called_once_with(email_tag_data['email_id'])

    @pytest.mark.asyncio
    async def _process_repair_email__ok_test(
            self,
            repair_tickets_monitor,
            make_inference_data,
            make_ticket,
            make_email
    ):
        email_id = 1234
        tagged_email = {"email_id": email_id, "tag_id": 1}
        email = make_email(email_id=email_id)
        inference_data = make_inference_data()
        service_number_site_map = {
            '1234': 'site_1',
            '2345': 'site_2',
        }

        tickets_created = [{'site_id': 'site_1', 'service_numbers': ['1234'], 'ticket_id': '5678'}]
        tickets_updated = [{'site_id': 'site_2', 'service_numbers': ['2345'], 'ticket_id': '1234'}]
        tickets_not_created = []

        create_ticket_response = (tickets_created, tickets_updated, tickets_not_created)
        existing_tickets_response = [make_ticket()]
        save_outputs_response = {'success': True}

        new_tagged_emails_repository = Mock()
        repair_tickets_monitor._new_tagged_emails_repository = new_tagged_emails_repository
        repair_tickets_monitor._new_tagged_emails_repository.get_email_details.return_value = email

        repair_tickets_monitor._get_inference = CoroutineMock(return_value=inference_data)
        repair_tickets_monitor._get_valid_service_numbers_site_map = CoroutineMock(return_value=service_number_site_map)
        repair_tickets_monitor._get_existing_tickets = CoroutineMock(return_value=existing_tickets_response)
        repair_tickets_monitor._create_tickets = CoroutineMock(return_value=create_ticket_response)
        repair_tickets_monitor._save_output = CoroutineMock(return_value=save_outputs_response)

        response = await repair_tickets_monitor._process_repair_email(tagged_email)

        repair_tickets_monitor._save_output.assert_awaited_once()
        new_tagged_emails_repository.mark_complete.assert_called_once_with(email_id)

        assert response is None

    @pytest.mark.asyncio
    async def _get_valid_service_numbers_site_map__ok_test(self, repair_tickets_monitor, make_rpc_response):
        client_id = '1234'
        potential_service_numbers = ['10111']
        site_id = '5678'
        verified_service_number_body = {'client_id': client_id, 'client_name': 'client_name', 'site_id': site_id}
        verified_service_number_response = make_rpc_response(status=200, body=verified_service_number_body)
        expected_result = {'10111': site_id}

        bruin_repository = Mock()
        bruin_repository.verify_service_number_information = CoroutineMock(
            return_value=verified_service_number_response
        )
        repair_tickets_monitor._bruin_repository = bruin_repository

        result = await repair_tickets_monitor._get_valid_service_numbers_site_map(client_id, potential_service_numbers)

        assert result == expected_result

    @pytest.mark.asyncio
    async def _get_valid_service_numbers_site_map__not_2XX_test(self, repair_tickets_monitor, make_rpc_response):
        client_id = '1234'
        potential_service_numbers = ['10111']
        site_id = '5678'
        verified_service_number_response = make_rpc_response(status=400, body="Error message")
        expected_result = {'10111': site_id}

        repair_tickets_monitor._bruin_repository.verify_service_number_information = CoroutineMock(
            return_value=verified_service_number_response
        )

        with pytest.raises(ResponseException):
            await repair_tickets_monitor._get_valid_service_numbers_site_map(client_id, potential_service_numbers)

    @pytest.mark.asyncio
    async def _get_existing_tickets__ok_test(
            self,
            repair_tickets_monitor,
            make_ticket,
            make_rpc_response,
    ):
        client_id = "1234"
        site_id = "5678"
        service_number_site_map = {"1234": site_id, "2345": site_id}
        open_ticket = make_ticket(client_id=client_id, ticket_id=1245)
        open_ticket['service_numbers'] = ["1234", "2345"]
        open_tickets_rpc_response = make_rpc_response(status=200, body=[open_ticket])

        expected_result = open_ticket.copy()
        expected_result['site_id'] = site_id
        expected_result = [expected_result]

        bruin_repository = Mock()
        bruin_repository.get_open_tickets_with_service_numbers = CoroutineMock(return_value=open_tickets_rpc_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        result = await repair_tickets_monitor._get_existing_tickets(client_id, service_number_site_map)

        assert result == expected_result

    @pytest.mark.asyncio
    async def _get_existing_tickets__404_test(
            self,
            repair_tickets_monitor,
            make_rpc_response,
    ):
        client_id = "1234"
        site_id = "5678"
        service_number_site_map = {"1234": site_id, "2345": site_id}
        open_tickets_rpc_response = make_rpc_response(status=404, body=[])

        expected_result = []

        bruin_repository = Mock()
        bruin_repository.get_open_tickets_with_service_numbers = CoroutineMock(return_value=open_tickets_rpc_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        result = await repair_tickets_monitor._get_existing_tickets(client_id, service_number_site_map)

        assert result == expected_result

    @pytest.mark.asyncio
    async def _get_existing_tickets__not_2XX_test(
            self,
            repair_tickets_monitor,
            make_rpc_response,
    ):
        client_id = "1234"
        site_id = "5678"
        service_number_site_map = {"1234": site_id, "2345": site_id}
        open_tickets_rpc_response = make_rpc_response(status=400, body=[])

        bruin_repository = Mock()
        bruin_repository.get_open_tickets_with_service_numbers = CoroutineMock(return_value=open_tickets_rpc_response)
        repair_tickets_monitor._bruin_repository = bruin_repository

        with pytest.raises(ResponseException):
            await repair_tickets_monitor._get_existing_tickets(client_id, service_number_site_map)

    def _get_potential_tickets__could_be_updated_tickets_test(
            self,
            repair_tickets_monitor,
            make_filter_flags,
            make_inference_data,
            make_rta_ticket_payload,
            existing_ticket_data_voo_with_service_numbers,
    ):
        predicted_class = "VOO"
        filter_flags = make_filter_flags(in_validation_set=True)
        site_id = existing_ticket_data_voo_with_service_numbers['site_id']
        existing_ticket = existing_ticket_data_voo_with_service_numbers
        service_number_site_map = {"1235": site_id, "4366": site_id}

        existing_tickets = [existing_ticket]
        inference_data = make_inference_data(
            predicted_class=predicted_class,
            filter_flags=filter_flags,
            potential_service_numbers=existing_ticket['service_numbers']
        )

        expected_tickets_could_be_updated = [
            make_rta_ticket_payload(
                site_id=site_id,
                service_numbers=existing_ticket['service_numbers'],
                ticket_id=str(existing_ticket['ticket_id']),
                not_created_reason="",
            )
        ]

        tickets_could_be_created, tickets_could_be_updated = repair_tickets_monitor._get_potential_tickets(
            inference_data,
            service_number_site_map,
            existing_tickets
        )

        assert tickets_could_be_created == []
        assert tickets_could_be_updated == expected_tickets_could_be_updated

    def _get_potential_tickets__could_be_created_tickets_test(
            self,
            repair_tickets_monitor,
            make_filter_flags,
            make_inference_data,
            make_rta_ticket_payload,
    ):
        predicted_class = "VOO"
        filter_flags = make_filter_flags(in_validation_set=True)
        site_id = "5678"
        service_numbers = ["1234", "2345"]
        service_number_site_map = {"1234": site_id, "2345": site_id}

        existing_tickets = []
        inference_data = make_inference_data(
            predicted_class=predicted_class,
            filter_flags=filter_flags,
            potential_service_numbers=service_numbers
        )

        expected_tickets_could_be_created = [
            make_rta_ticket_payload(
                site_id="5678",
                service_numbers=service_numbers,
                ticket_id="",
                not_created_reason="",
            )
        ]

        tickets_could_be_created, tickets_could_be_updated = repair_tickets_monitor._get_potential_tickets(
            inference_data,
            service_number_site_map,
            existing_tickets
        )

        assert tickets_could_be_created == expected_tickets_could_be_created
        assert tickets_could_be_updated == []

    def _get_class_other_tickets_test(self, repair_tickets_monitor):
        service_number_site_map = {"1234": "4578"}

        expected_tickets = [{
            "site_id": "4578",
            "service_numbers": ["1234"],
            "not_creation_reason": "predicted class is Other",
            "ticket_id": ""
        }]

        result_tickets = repair_tickets_monitor._get_class_other_tickets(service_number_site_map)

        assert expected_tickets == result_tickets

    def _create_output_ticket_dict_test(
            self,
            repair_tickets_monitor,
    ):
        site_id = "1234"
        service_numbers = ["1234", "5678"]
        ticket_id = "1234"
        reason = "Test"

        expected = {
            'site_id': site_id,
            'service_numbers': service_numbers,
            'ticket_id': ticket_id,
            'not_creation_reason': reason
        }
        result = repair_tickets_monitor._create_output_ticket_dict(site_id, service_numbers, ticket_id, reason)

        assert result == expected

    @pytest.mark.parametrize(
        'ticket, site_ids, predicted_class,expected',
        [
            ({"site_id": "1234", "category": "Other"}, {"1234"}, "VAS", False),
            ({"site_id": "5890", "category": "VOO"}, {"1234"}, "VAS", False),
            ({"site_id": "1234", "category": "VAS"}, {"1234"}, "VAS", True),
            ({"site_id": "1234", "category": "VOO"}, {"1234"}, "VOO", True),
            ({"site_id": "1234", "category": "VAS"}, {"1234"}, "VOO", False),
            ({"site_id": "1234", "category": "VOO"}, {"1234"}, "VAS", True),
        ]
    )
    def _should_update_ticket_test(
            self,
            repair_tickets_monitor,
            ticket,
            site_ids,
            predicted_class,
            expected
    ):
        result = repair_tickets_monitor._should_update_ticket(ticket, site_ids, predicted_class)
        assert result == expected

    @pytest.mark.parametrize(
        'predicted_class, filter_flags, expected',
        [
            (
                    "Other",
                    {
                        "is_filtered": False,
                        "in_validation_set": False,
                        "tagger_is_below_threshold": False,
                        "rta_model1_is_below_threshold": False,
                        "rta_model2_is_below_threshold": False,
                    }, False
            ),
            (
                    "VOO",
                    {
                        "is_filtered": True,
                        "in_validation_set": False,
                        "tagger_is_below_threshold": False,
                        "rta_model1_is_below_threshold": False,
                        "rta_model2_is_below_threshold": False,
                    }, False
            ),
            (
                    "VOO",
                    {
                        "is_filtered": False,
                        "in_validation_set": True,
                        "tagger_is_below_threshold": False,
                        "rta_model1_is_below_threshold": False,
                        "rta_model2_is_below_threshold": False,
                    }, False
            ),
            (
                    "VAS",
                    {
                        "is_filtered": False,
                        "in_validation_set": False,
                        "tagger_is_below_threshold": True,
                        "rta_model1_is_below_threshold": False,
                        "rta_model2_is_below_threshold": False,
                    }, False
            ),
            (
                    "VAS",
                    {
                        "is_filtered": False,
                        "in_validation_set": False,
                        "tagger_is_below_threshold": False,
                        "rta_model1_is_below_threshold": True,
                        "rta_model2_is_below_threshold": False,
                    }, False
            ),
            (
                    "VOO",
                    {
                        "is_filtered": False,
                        "in_validation_set": False,
                        "tagger_is_below_threshold": False,
                        "rta_model1_is_below_threshold": False,
                        "rta_model2_is_below_threshold": True,
                    }, False
            ),
            (
                    "VAS",
                    {
                        "is_filtered": False,
                        "in_validation_set": False,
                        "tagger_is_below_threshold": False,
                        "rta_model1_is_below_threshold": False,
                        "rta_model2_is_below_threshold": False,
                    }, True
            ),
        ]
    )
    def _is_inference_actionable_test(
            self,
            repair_tickets_monitor,
            predicted_class,
            filter_flags,
            expected,
    ):
        inference_data = {"filter_flags": filter_flags, "predicted_class": predicted_class}

        result = repair_tickets_monitor._is_inference_actionable(inference_data)
        assert result == expected
