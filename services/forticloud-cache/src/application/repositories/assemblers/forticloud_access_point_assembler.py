import logging

from application.clients.models import AccessPoint

logger = logging.getLogger(__name__)


def build_access_point_list_to_cache(modeled_access_points_list, network_id):
    access_point_list_to_cache = []
    for modeled_access_point in modeled_access_points_list:
        access_point_list_to_cache.append(
            {
                "serial_number": modeled_access_point.serial_number,
                "network_id": network_id,
            }
        )
    return access_point_list_to_cache


def get_access_points_modeled(access_points_list):
    modeled_access_points = []
    for access_point in access_points_list:
        try:
            modeled_access_points.append(AccessPoint(**access_point))
        except Exception as e:
            logger.warning(f"Can't apply access point model to: {access_point} because {e}")
    return modeled_access_points
