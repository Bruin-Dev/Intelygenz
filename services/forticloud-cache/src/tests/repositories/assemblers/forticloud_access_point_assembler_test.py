from application.models.models import AccessPoint
from application.repositories.assemblers import forticloud_access_point_assembler

mock_access_point_1 = {"connection_state": "connected", "serial": "sn_2"}
mock_access_point_2 = {"connection_state": "disconnected", "serial": "sn_1"}

mock_list_of_access_point = [mock_access_point_1, mock_access_point_2]
bad_mock_access_point = {"connection_state": "online"}
mock_list_with_only_bad_access_point = [bad_mock_access_point]
network_id = 1
mock_list_of_access_point_modeled = [AccessPoint(**mock_access_point_1), AccessPoint(**mock_access_point_2)]


def get_access_points_modeled_return_not_none_test():
    access_point_modeled = forticloud_access_point_assembler.get_access_points_modeled(mock_list_of_access_point)
    assert access_point_modeled is not None


def get_access_points_modeled_return_a_list_test():
    access_point_modeled = forticloud_access_point_assembler.get_access_points_modeled(mock_list_of_access_point)
    assert type(access_point_modeled) is list


def get_access_points_modeled_return_some_elements_test():
    access_point_modeled = forticloud_access_point_assembler.get_access_points_modeled(mock_list_of_access_point)
    assert len(access_point_modeled) > 0


def get_access_points_modeled_return_empty_list_when_can_not_apply_model_test():
    access_point_modeled = forticloud_access_point_assembler.get_access_points_modeled(
        mock_list_with_only_bad_access_point
    )
    assert len(access_point_modeled) == 0


def build_access_point_list_to_cache_return_not_none_test():
    access_point_modeled = forticloud_access_point_assembler.build_access_point_list_to_cache(
        mock_list_of_access_point_modeled, network_id
    )
    assert access_point_modeled is not None


def build_access_point_list_to_cache_return_list_test():
    access_point_modeled = forticloud_access_point_assembler.build_access_point_list_to_cache(
        mock_list_of_access_point_modeled, network_id
    )
    assert type(access_point_modeled) is list


def build_access_point_list_to_cache_return_not_empty_list_test():
    access_point_modeled = forticloud_access_point_assembler.build_access_point_list_to_cache(
        mock_list_of_access_point_modeled, network_id
    )
    assert len(access_point_modeled) > 0
