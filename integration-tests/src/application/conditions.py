import asyncio
import logging
from typing import Dict

log = logging.getLogger(__name__)
_path_conditions: Dict[str, asyncio.Condition] = {}


async def wait_for_path(path: str, timeout: float):
    """
    Makes the current Task wait for a path condition to be notified.
    :param path: the path to be waited for
    :param timeout: the maximum time to wait for the condition to be notified.
    :return:
    """
    log.debug(f"for_route(path={path}, timeout={timeout})")
    global _path_conditions
    condition = asyncio.Condition()
    _path_conditions[path] = condition
    async with condition:
        try:
            log.debug(f"for_route(): wait_for={condition}")
            await asyncio.wait_for(condition.wait(), timeout)
        except asyncio.exceptions.TimeoutError:
            raise TimeoutError(f"Timed out waiting for {path}")


async def path_was_reached(path: str):
    """
    Notifies the path condition and wakes up the tasks waiting for it
    :param path: the path being reached
    """
    log.debug(f"route_reached(path={path})")
    global _path_conditions
    if path in _path_conditions:
        condition = _path_conditions[path]
        async with condition:
            log.debug(f"route_reached(): notifying condition={condition}")
            condition.notify_all()
