import logging

from application.clients.models import Switch

logger = logging.getLogger(__name__)


def build_switch_list_to_cache(switch_list):
    switch_list_to_cache = []
    for switch in switch_list:
        switch_list_to_cache.append(
            {
                "serial_number": switch.serial_number,
                "network_id": switch.network_id,
            }
        )
    return switch_list_to_cache


def get_switches_modeled(switches_list):
    modeled_switches = []
    for switch in switches_list:
        try:
            modeled_switches.append(Switch(**switch))
        except Exception as e:
            logger.warning(f"Can't apply switch model to: {switch} because {e}")
    return modeled_switches
