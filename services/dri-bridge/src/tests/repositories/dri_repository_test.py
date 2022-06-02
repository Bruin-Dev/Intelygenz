from unittest.mock import Mock

import pytest
from application.repositories.dri_repository import DRIRepository
from asynctest import CoroutineMock


class TestBruinRepository:
    def instance_test(self):
        logger = Mock()
        storage_repo = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)

        assert dri_repository._logger == logger
        assert dri_repository._storage_repository == storage_repo
        assert dri_repository._dri_client == dri_client

    @pytest.mark.asyncio
    async def get_dri_parameters_ok_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_return = {"body": "1720079", "status": 200}
        get_task_results_return = {
            "body": {"InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers": "ATT"},
            "status": 200,
        }
        logger = Mock()
        storage_repo = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        dri_repository._get_task_id = CoroutineMock(return_value=task_id_return)
        dri_repository._get_task_results = CoroutineMock(return_value=get_task_results_return)

        task_id_status_return = await dri_repository.get_dri_parameters(serial, parameter_set)
        dri_repository._get_task_id.assert_awaited_once_with(serial, parameter_set)
        dri_repository._get_task_results.assert_awaited_once_with(serial, task_id_return["body"])
        assert task_id_status_return == get_task_results_return

    @pytest.mark.asyncio
    async def get_dri_parameters_ko_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_return = {"body": "Failed", "status": 400}

        logger = Mock()
        storage_repo = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        dri_repository._get_task_id = CoroutineMock(return_value=task_id_return)
        dri_repository._get_task_results = CoroutineMock()

        task_id_status_return = await dri_repository.get_dri_parameters(serial, parameter_set)
        dri_repository._get_task_id.assert_awaited_once_with(serial, parameter_set)
        dri_repository._get_task_results.assert_not_awaited()
        assert task_id_status_return == task_id_return

    @pytest.mark.asyncio
    async def get_task_id_redis_task_id_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_return = "1720079"

        storage_repo = Mock()
        storage_repo.get = Mock(return_value=task_id_return)
        storage_repo.save = Mock()

        logger = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        dri_repository._get_pending_task_ids = CoroutineMock()
        dri_repository._get_task_id_from_dri = CoroutineMock()

        task_id_response = await dri_repository._get_task_id(serial, parameter_set)

        storage_repo.get.assert_called_once_with(serial)
        dri_repository._get_pending_task_ids.assert_not_awaited()
        storage_repo.save.assert_not_called()
        dri_repository._get_task_id_from_dri.assert_not_awaited()
        assert task_id_response == {"body": task_id_return, "status": 200}

    @pytest.mark.asyncio
    async def get_task_id_failed_pending_task_id_rpc_call_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        pending_task_response = {"body": "Failed", "status": 400}

        storage_repo = Mock()
        storage_repo.get = Mock(return_value=None)
        storage_repo.save = Mock()

        logger = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        dri_repository._get_pending_task_ids = CoroutineMock(return_value=pending_task_response)
        dri_repository._get_task_id_from_dri = CoroutineMock()

        task_id_response = await dri_repository._get_task_id(serial, parameter_set)

        storage_repo.get.assert_called_once_with(serial)
        dri_repository._get_pending_task_ids.assert_awaited_once_with(serial)
        storage_repo.save.assert_not_called()
        dri_repository._get_task_id_from_dri.assert_not_awaited()
        assert task_id_response == pending_task_response

    @pytest.mark.asyncio
    async def get_task_id_pending_task_id_len_greater_than_zero_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_return = "1720079"
        task_id_return_1 = "123"

        pending_task_response = {"body": [task_id_return, task_id_return_1], "status": 200}

        storage_repo = Mock()
        storage_repo.get = Mock(return_value=None)
        storage_repo.save = Mock()

        logger = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        dri_repository._get_pending_task_ids = CoroutineMock(return_value=pending_task_response)
        dri_repository._get_task_id_from_dri = CoroutineMock()

        task_id_response = await dri_repository._get_task_id(serial, parameter_set)

        storage_repo.get.assert_called_once_with(serial)
        dri_repository._get_pending_task_ids.assert_awaited_once_with(serial)
        storage_repo.save.assert_called_once_with(serial, task_id_return)
        dri_repository._get_task_id_from_dri.assert_not_awaited()
        assert task_id_response == {"body": task_id_return, "status": pending_task_response["status"]}

    @pytest.mark.asyncio
    async def get_task_id_pending_task_id_len_equals_zero_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_return = "1720079"

        pending_task_response = {"body": [], "status": 200}
        task_id_from_dri_response = {"body": task_id_return, "status": 200}

        storage_repo = Mock()
        storage_repo.get = Mock(return_value=None)
        storage_repo.save = Mock()

        logger = Mock()
        dri_client = Mock()

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        dri_repository._get_pending_task_ids = CoroutineMock(return_value=pending_task_response)
        dri_repository._get_task_id_from_dri = CoroutineMock(return_value=task_id_from_dri_response)

        task_id_response = await dri_repository._get_task_id(serial, parameter_set)

        storage_repo.get.assert_called_once_with(serial)
        dri_repository._get_pending_task_ids.assert_awaited_once_with(serial)
        storage_repo.save.assert_not_called()
        dri_repository._get_task_id_from_dri.assert_awaited_once_with(serial, parameter_set)
        assert task_id_response == task_id_from_dri_response

    @pytest.mark.asyncio
    async def get_task_id_from_dri_ok_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_return = "1720079"
        task_id_from_dri_response = {
            "body": {
                "status": "SUCCESS",
                "message": "All Good!",
                "data": {"Id": task_id_return, "ErrorCode": 100, "Message": ""},
            },
            "status": 200,
        }

        logger = Mock()

        storage_repo = Mock()
        storage_repo.save = Mock()

        dri_client = Mock()
        dri_client.get_task_id = CoroutineMock(return_value=task_id_from_dri_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_id_from_dri = await dri_repository._get_task_id_from_dri(serial, parameter_set)
        dri_client.get_task_id.assert_awaited_once_with(serial, parameter_set)
        storage_repo.save.assert_called_once_with(serial, task_id_return)
        assert task_id_from_dri == {"body": task_id_return, "status": task_id_from_dri_response["status"]}

    @pytest.mark.asyncio
    async def get_task_id_from_dri_ko_failed_rpc_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        task_id_from_dri_response = {"body": "Failed", "status": 400}

        logger = Mock()

        storage_repo = Mock()
        storage_repo.save = Mock()

        dri_client = Mock()
        dri_client.get_task_id = CoroutineMock(return_value=task_id_from_dri_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_id_from_dri = await dri_repository._get_task_id_from_dri(serial, parameter_set)
        dri_client.get_task_id.assert_awaited_once_with(serial, parameter_set)
        storage_repo.save.assert_not_called()
        assert task_id_from_dri == task_id_from_dri_response

    @pytest.mark.asyncio
    async def get_task_id_from_dri_ko_200_failed_status_test(self):
        serial = "700059"
        parameter_set = {
            "ParameterNames": [
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum",
                "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei",
                "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress",
            ],
            "Source": 0,
        }

        dri_task_id_body = {
            "status": "FAILED",
            "message": "All Good!",
            "data": {"Id": 1725608, "ErrorCode": 100, "Message": ""},
        }
        task_id_from_dri_response = {"body": dri_task_id_body, "status": 200}

        get_task_id_from_dri_return_dict = {"body": dri_task_id_body, "status": 400}
        logger = Mock()

        storage_repo = Mock()
        storage_repo.save = Mock()

        dri_client = Mock()
        dri_client.get_task_id = CoroutineMock(return_value=task_id_from_dri_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_id_from_dri = await dri_repository._get_task_id_from_dri(serial, parameter_set)
        dri_client.get_task_id.assert_awaited_once_with(serial, parameter_set)
        storage_repo.save.assert_not_called()
        assert task_id_from_dri == get_task_id_from_dri_return_dict

    @pytest.mark.asyncio
    async def get_task_results_ok_completed_test(self):
        serial = "700059"
        task_id = "1720079"

        parameter_name = "InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei"
        parameter_value = "864839040023968"
        get_tasks_result_response = {
            "body": {
                "status": "SUCCESS",
                "message": "All Good!",
                "data": {
                    "Parameters": [{"Name": parameter_name, "Value": parameter_value, "ErrorCode": 100, "Message": ""}],
                    "ErrorCode": 100,
                    "Message": "",
                },
            },
            "status": 200,
        }
        logger = Mock()

        storage_repo = Mock()
        storage_repo.remove = Mock()

        dri_client = Mock()
        dri_client.get_task_results = CoroutineMock(return_value=get_tasks_result_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_results_response = await dri_repository._get_task_results(serial, task_id)
        dri_client.get_task_results.assert_awaited_once_with(serial, task_id)
        storage_repo.remove.assert_not_called()
        assert task_results_response == {"body": {parameter_name: parameter_value}, "status": 200}

    @pytest.mark.asyncio
    async def get_task_results_ok_pending_test(self):
        serial = "700059"
        task_id = "1720079"

        get_tasks_result_response = {
            "body": {
                "status": "SUCCESS",
                "message": "All Good!",
                "data": {"Parameters": [], "ErrorCode": 100, "Message": "Pending"},
            },
            "status": 200,
        }
        logger = Mock()

        storage_repo = Mock()
        storage_repo.remove = Mock()

        dri_client = Mock()
        dri_client.get_task_results = CoroutineMock(return_value=get_tasks_result_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_results_response = await dri_repository._get_task_results(serial, task_id)
        dri_client.get_task_results.assert_awaited_once_with(serial, task_id)
        storage_repo.remove.assert_not_called()
        assert task_results_response == {
            "body": f"Data is still being fetched from DRI for serial {serial}",
            "status": 204,
        }

    @pytest.mark.asyncio
    async def get_task_results_ko_rejected_test(self):
        serial = "700059"
        task_id = "1720079"

        get_tasks_result_response = {
            "body": {
                "status": "SUCCESS",
                "message": "All Good!",
                "data": {"Parameters": [], "ErrorCode": 100, "Message": "Rejected"},
            },
            "status": 200,
        }
        logger = Mock()

        storage_repo = Mock()
        storage_repo.remove = Mock()

        dri_client = Mock()
        dri_client.get_task_results = CoroutineMock(return_value=get_tasks_result_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_results_response = await dri_repository._get_task_results(serial, task_id)
        dri_client.get_task_results.assert_awaited_once_with(serial, task_id)
        storage_repo.remove.assert_called_once_with(serial)
        assert task_results_response == {"body": f"DRI task was rejected for serial {serial}", "status": 403}

    @pytest.mark.asyncio
    async def get_task_results_ko_relogin_error_test(self):
        serial = "700059"
        task_id = "1720079"

        get_tasks_result_response = {"body": "Got 401 from DRI", "status": 401}
        logger = Mock()

        storage_repo = Mock()
        storage_repo.remove = Mock()

        dri_client = Mock()
        dri_client.get_task_results = CoroutineMock(return_value=get_tasks_result_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_results_response = await dri_repository._get_task_results(serial, task_id)
        dri_client.get_task_results.assert_awaited_once_with(serial, task_id)
        storage_repo.remove.assert_not_called()
        assert task_results_response == get_tasks_result_response

    @pytest.mark.asyncio
    async def get_task_results_ko_200_failed_test(self):
        serial = "700059"
        task_id = "1720079"

        dri_task_results_response = {
            "body": {"status": "FAILED", "message": "There are no tasks in transaction ID=1720079"},
            "status": 200,
        }
        get_tasks_result_response = {"body": f"Failed to retrieve data from DRI for serial {serial}", "status": 400}
        logger = Mock()

        storage_repo = Mock()
        storage_repo.remove = Mock()

        dri_client = Mock()
        dri_client.get_task_results = CoroutineMock(return_value=dri_task_results_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_results_response = await dri_repository._get_task_results(serial, task_id)
        dri_client.get_task_results.assert_awaited_once_with(serial, task_id)
        storage_repo.remove.assert_called_once_with(serial)
        assert task_results_response == get_tasks_result_response

    @pytest.mark.asyncio
    async def get_task_results_ko_general_error_test(self):
        serial = "700059"
        task_id = "1720079"

        get_tasks_result_response = {"body": f"Failed to retrieve data from DRI for serial {serial}", "status": 400}
        logger = Mock()

        storage_repo = Mock()
        storage_repo.remove = Mock()

        dri_client = Mock()
        dri_client.get_task_results = CoroutineMock(return_value=get_tasks_result_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        task_results_response = await dri_repository._get_task_results(serial, task_id)
        dri_client.get_task_results.assert_awaited_once_with(serial, task_id)
        storage_repo.remove.assert_called_once_with(serial)
        assert task_results_response == get_tasks_result_response

    @pytest.mark.asyncio
    async def get_pending_task_ids_ok_test(self):
        serial = "700059"

        pending_task_list = [{"Id": "233"}, {"Id": "2432"}]
        pending_task_ids_response = {
            "body": {
                "status": "SUCCESS",
                "message": "All Good!",
                "data": {"Transactions": pending_task_list, "ErrorCode": 100, "Message": ""},
            },
            "status": 200,
        }

        pending_task_list_body = [task["Id"] for task in pending_task_list]
        logger = Mock()
        storage_repo = Mock()

        dri_client = Mock()
        dri_client.get_pending_task_ids = CoroutineMock(return_value=pending_task_ids_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        pending_task_response = await dri_repository._get_pending_task_ids(serial)
        dri_client.get_pending_task_ids.assert_awaited_once_with(serial)
        assert pending_task_response == {"body": pending_task_list_body, "status": 200}

    @pytest.mark.asyncio
    async def get_pending_task_ids_ko_failed_rpc_test(self):
        serial = "700059"

        pending_task_ids_response = {"body": "Failed", "status": 400}

        logger = Mock()
        storage_repo = Mock()

        dri_client = Mock()
        dri_client.get_pending_task_ids = CoroutineMock(return_value=pending_task_ids_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        pending_task_response = await dri_repository._get_pending_task_ids(serial)
        dri_client.get_pending_task_ids.assert_awaited_once_with(serial)
        assert pending_task_response == pending_task_ids_response

    @pytest.mark.asyncio
    async def get_pending_task_ids_ko_200_failed_test(self):
        serial = "700059"

        pending_task_from_dri_body = {
            "status": "FAILED",
            "message": "All Good!",
            "data": {"Transactions": [], "ErrorCode": 100, "Message": ""},
        }

        pending_task_from_dri_response = {"body": pending_task_from_dri_body, "status": 200}
        pending_task_ids_response = {"body": pending_task_from_dri_body, "status": 400}

        logger = Mock()
        storage_repo = Mock()

        dri_client = Mock()
        dri_client.get_pending_task_ids = CoroutineMock(return_value=pending_task_from_dri_response)

        dri_repository = DRIRepository(logger, storage_repo, dri_client)
        pending_task_response = await dri_repository._get_pending_task_ids(serial)
        dri_client.get_pending_task_ids.assert_awaited_once_with(serial)
        assert pending_task_response == pending_task_ids_response
