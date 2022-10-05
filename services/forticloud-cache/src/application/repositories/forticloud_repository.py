from application.repositories.assemblers import (
    forticloud_access_point_assembler,
    forticloud_networks_assembler,
    forticloud_switch_assembler,
)


class ForticloudRepository:
    def __init__(self, forticloud_client):
        self.forticloud_client = forticloud_client

    async def get_list_networks_ids(self):

        networks_list = await self.forticloud_client.get_networks()
        modeled_networks_list = forticloud_networks_assembler.get_networks_modeled(networks_list)
        id_networks_list = forticloud_networks_assembler.build_networks_ids_list(modeled_networks_list)
        return id_networks_list

    async def get_list_switches(self, id_networks_list):
        list_of_switches = []

        for id_network in id_networks_list:
            switches = await self.forticloud_client.get_switches(id_network)
            list_of_switches += forticloud_switch_assembler.build_switch_list_to_cache(
                forticloud_switch_assembler.get_switches_modeled(switches)
            )
        return list_of_switches

    async def get_list_access_point(self, id_networks_list):
        list_of_access_points = []

        for network_id in id_networks_list:
            access_points = await self.forticloud_client.get_access_points(network_id)
            list_of_access_points += forticloud_access_point_assembler.build_access_point_list_to_cache(
                forticloud_access_point_assembler.get_access_points_modeled(access_points), network_id
            )
        return list_of_access_points
