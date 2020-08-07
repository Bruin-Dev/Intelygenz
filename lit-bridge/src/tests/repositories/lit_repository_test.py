import datetime
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from application.repositories.lit_repository import LitRepository
from apscheduler.util import undefined

from application.repositories import lit_repository as lit_repo_module
from config import testconfig as config


class TestLitRepository:

    def instance_test(self):
        lit_client = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)

        assert lit_repo._lit_client == lit_client
        assert lit_repo._logger == logger
        assert lit_repo._scheduler == scheduler
        assert lit_repo._config == config

    def login_job_false_exec_on_start_test(self):
        lit_client = Mock()
        lit_client.login = Mock()
        logger = Mock()
        scheduler = Mock()
        configs = config
        redis_client = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, configs, redis_client)
        with patch.object(lit_repo_module, 'timezone', new=Mock()):
            lit_repo.login_job()

        scheduler.add_job.assert_called_once_with(
            lit_client.login, 'interval',
            minutes=configs.LIT_CONFIG['login_ttl'],
            next_run_time=undefined,
            replace_existing=True,
            id='login',
        )

    def login_job_true_exec_on_start_test(self):
        lit_client = Mock()
        lit_client.login = Mock()
        logger = Mock()
        scheduler = Mock()
        configs = config
        redis_client = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, configs, redis_client)
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)

        with patch.object(lit_repo_module, 'datetime', new=datetime_mock):
            with patch.object(lit_repo_module, 'timezone', new=Mock()):
                lit_repo.login_job(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            lit_client.login, 'interval',
            minutes=configs.LIT_CONFIG['login_ttl'],
            next_run_time=next_run_time,
            replace_existing=True,
            id='login',
        )

    def create_dispatch_test(self):
        lit_client = Mock()
        lit_client.create_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)
        lit_repo.create_dispatch(payload)

        lit_client.create_dispatch.assert_called_with(payload)

    def cancel_dispatch_test(self):
        lit_client = Mock()
        lit_client.cancel_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        payload = {"dispatch_number": "D123"}

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)
        lit_repo.cancel_dispatch(payload)

        lit_client.cancel_dispatch.assert_called_with(payload)

    def get_dispatch_test(self):
        lit_client = Mock()
        lit_client.get_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        dispatch_number = "D123"
        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)
        lit_repo.get_dispatch(dispatch_number)

        lit_client.get_dispatch.assert_called_with(dispatch_number)

    def get_all_dispatches_test(self):
        lit_client = Mock()
        lit_client.get_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)
        lit_repo.get_all_dispatches()

        lit_client.get_all_dispatches.assert_called_once()

    def update_dispatch_test(self):
        lit_client = Mock()
        lit_client.update_dispatch = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)
        lit_repo.update_dispatch(payload)

        lit_client.update_dispatch.assert_called_with(payload)

    def upload_file_test(self):
        lit_client = Mock()
        lit_client.upload_file = Mock()

        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        payload = {"Request_Dispatch": {"test": "dispatch"}}
        dispatch_number = "D123"
        file_name = "test.pdf"
        file_content = "application/pdf"

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)
        lit_repo.upload_file(dispatch_number, payload, file_name, file_content)

        lit_client.upload_file.assert_called_with(dispatch_number, payload, file_name, file_content)

    def filter_dispatches_test(self):
        lit_client = Mock()
        logger = Mock()
        scheduler = Mock()
        config = Mock()
        redis_client = Mock()

        dispatch_number_1 = 'DIS55401'
        ticket_id_1 = '4661997'
        dispatch_1 = {
            "turn_up": None,
            "Time_Zone_Local": "Pacific Time",
            "Time_of_Check_Out": None,
            "Time_of_Check_In": None,
            "Tech_Off_Site": False,
            "Tech_Mobile_Number": None,
            "Tech_First_Name": None,
            "Tech_Arrived_On_Site": False,
            "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "Special_Dispatch_Notes": False,
            "Site_Survey_Quote_Required": False,
            "Scope_of_Work": "Device is bouncing constantly TEST LUNES",
            "Name_of_MetTel_Requester": "Karen Doe",
            "MetTel_Tech_Call_In_Instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "MetTel_Requester_Email": "karen.doe@mettel.net",
            "MetTel_Note_Updates": None,
            "MetTel_Group_Email": None,
            "MetTel_Department_Phone_Number": "+1 666 6666 666",
            "MetTel_Department": "Customer Care",
            "MetTel_Bruin_TicketID": ticket_id_1,
            "Local_Time_of_Dispatch": None,
            "Job_Site_Zip_Code": "99088",
            "Job_Site_Street": "123 Fake Street",
            "Job_Site_State": "CA",
            "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
            "Job_Site_City": "Pleasantown",
            "Job_Site": "TEST-Red Rose Inn",
            "Information_for_Tech": None,
            "Hard_Time_of_Dispatch_Time_Zone_Local": None,
            "Hard_Time_of_Dispatch_Local": None,
            "Dispatch_Status": "New Dispatch",
            "Dispatch_Number": dispatch_number_1,
            "Date_of_Dispatch": "2019-11-14",
            "Close_Out_Notes": None,
            "Backup_MetTel_Department_Phone_Number": None
        }
        dispatch_number_2 = 'DIS55402'
        ticket_id_2 = '4662970'
        dispatch_2 = {
            "turn_up": None,
            "Time_Zone_Local": "Hawaii Time",
            "Time_of_Check_Out": None,
            "Time_of_Check_In": None,
            "Tech_Off_Site": False,
            "Tech_Mobile_Number": None,
            "Tech_First_Name": None,
            "Tech_Arrived_On_Site": False,
            "Special_Materials_Needed_for_Dispatch": "materials",
            "Special_Dispatch_Notes": None,
            "Site_Survey_Quote_Required": False,
            "Scope_of_Work": "issues",
            "Name_of_MetTel_Requester": "JC Req lastnr",
            "MetTel_Tech_Call_In_Instructions": "instructions",
            "MetTel_Requester_Email": "mettel@mettel.com",
            "MetTel_Note_Updates": None,
            "MetTel_Group_Email": None,
            "MetTel_Department_Phone_Number": "+16666666666",
            "MetTel_Department": "Provisioning",
            "MetTel_Bruin_TicketID": ticket_id_2,
            "Local_Time_of_Dispatch": None,
            "Job_Site_Zip_Code": "90024",
            "Job_Site_Street": "1419 Westwood Blvd asdfasdf",
            "Job_Site_State": "California",
            "Job_Site_Contact_Name_and_Phone_Number": "TEST PEPE PEpe +16666666666",
            "Job_Site_City": "Los Angeles",
            "Job_Site": "TEST-JC",
            "Information_for_Tech": None,
            "Hard_Time_of_Dispatch_Time_Zone_Local": None,
            "Hard_Time_of_Dispatch_Local": None,
            "Dispatch_Status": "New Dispatch",
            "Dispatch_Number": dispatch_number_2,
            "Date_of_Dispatch": "2020-05-28",
            "Close_Out_Notes": None,
            "Backup_MetTel_Department_Phone_Number": None
        }

        redis_get_mock = [dispatch_1, None]
        redis_client.get = Mock(side_effect=redis_get_mock)

        lit_repo = LitRepository(lit_client, logger, scheduler, config, redis_client)

        all_dispatches = {
            "DispatchList": [
                dispatch_1,
                dispatch_2
            ]
        }

        expected_filtered_dispatches = [dispatch_1]

        response = lit_repo.filter_dispatches(all_dispatches)

        assert response == expected_filtered_dispatches
