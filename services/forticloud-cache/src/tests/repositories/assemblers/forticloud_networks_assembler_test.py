from application.models.models import Network
from application.repositories.assemblers import forticloud_networks_assembler

mock_network_example_1 = {"oid": 1, "name": "network_1"}
mock_network_example_2 = {"oid": 2, "name": "network_2"}
network_example_1 = Network(**mock_network_example_1)
network_example_2 = Network(**mock_network_example_2)
list_of_networks_modeled = [network_example_1, network_example_2]
list_of_networks = [mock_network_example_1, mock_network_example_2]
bad_mock_network_example = {"oid": 2}
mock_list_with_only_bad_network = [bad_mock_network_example]


def build_networks_ids_list_return_not_none_test():
    id_networks_list = forticloud_networks_assembler.build_networks_ids_list(list_of_networks_modeled)
    assert id_networks_list is not None


def build_networks_ids_list_return_a_list_test():
    id_networks_list = forticloud_networks_assembler.build_networks_ids_list(list_of_networks_modeled)
    assert type(id_networks_list) is list


def build_networks_ids_list_return_some_items_test():
    id_networks_list = forticloud_networks_assembler.build_networks_ids_list(list_of_networks_modeled)
    assert len(id_networks_list) > 0


def get_networks_modeled_return_not_none_test():
    networks_modeled = forticloud_networks_assembler.get_networks_modeled(list_of_networks)
    assert networks_modeled is not None


def get_networks_modeled_return_a_list_test():
    networks_modeled = forticloud_networks_assembler.get_networks_modeled(list_of_networks)
    assert type(networks_modeled) is list


def get_networks_modeled_return_some_elements_test():
    networks_modeled = forticloud_networks_assembler.get_networks_modeled(list_of_networks)
    assert len(networks_modeled) > 0


def get_networks_modeled_return_empty_list_when_can_not_apply_model_test():
    networks_modeled = forticloud_networks_assembler.get_networks_modeled(bad_mock_network_example)
    assert len(networks_modeled) == 0
