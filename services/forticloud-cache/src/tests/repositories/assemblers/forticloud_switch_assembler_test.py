from application.models.models import Switch
from application.repositories.assemblers import forticloud_switch_assembler

mock_switch_1 = {"network": 1, "sn": "serial_number_test_1", "status": "offline"}
mock_switch_2 = {"network": 2, "sn": "serial_number_test_2", "status": "online"}
mock_list_of_switches = [mock_switch_1, mock_switch_2]
bad_mock_switch_2 = {"network": 2}
bad_mock_list_of_switches = [bad_mock_switch_2]
mock_list_of_switches_modeled = [Switch(**mock_switch_1), Switch(**mock_switch_2)]


def get_switches_modeled_return_not_none_test():
    access_point_modeled = forticloud_switch_assembler.get_switches_modeled(mock_list_of_switches)
    assert access_point_modeled is not None


def get_switches_modeled_return_a_list_test():
    access_point_modeled = forticloud_switch_assembler.get_switches_modeled(mock_list_of_switches)
    assert type(access_point_modeled) is list


def get_switches_modeled_return_some_elements_test():
    access_point_modeled = forticloud_switch_assembler.get_switches_modeled(mock_list_of_switches)
    assert len(access_point_modeled) > 0


def get_switches_modeled_return_empty_list_when_can_not_apply_model_test():
    access_point_modeled = forticloud_switch_assembler.get_switches_modeled(bad_mock_list_of_switches)
    assert len(access_point_modeled) == 0


def build_switch_list_to_cache_return_not_none_test():
    access_point_modeled = forticloud_switch_assembler.build_switch_list_to_cache(mock_list_of_switches_modeled)
    assert access_point_modeled is not None


def build_switch_list_to_cache_return_list_test():
    access_point_modeled = forticloud_switch_assembler.build_switch_list_to_cache(mock_list_of_switches_modeled)
    assert type(access_point_modeled) is list


def build_switch_list_to_cache_return_not_empty_list_test():
    access_point_modeled = forticloud_switch_assembler.build_switch_list_to_cache(mock_list_of_switches_modeled)
    assert len(access_point_modeled) > 0
