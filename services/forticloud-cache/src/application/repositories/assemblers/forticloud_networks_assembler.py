import logging

from application.clients.models import Network

logger = logging.getLogger(__name__)


def build_networks_ids_list(networks_list):
    id_networks_list = []
    for network in networks_list:
        id_networks_list.append(network.id)
    return id_networks_list


def get_networks_modeled(network_list):
    modeled_networks = []
    for network in network_list:
        try:
            modeled_networks.append(Network(**network))
        except Exception as e:
            logger.warning(f"Can't apply network model to: {network} because {e}")
    return modeled_networks
