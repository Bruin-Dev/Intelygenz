import logging
from typing import Any, Awaitable, Callable, Dict, Optional

from application.conditions import path_was_reached, wait_for_path
from application.handler import DoNothing, Handler, WillExecute, WillReturn
from dataclasses import dataclass
from starlette.responses import JSONResponse
from starlette.routing import Match
from starlette.routing import Route as Matcher

log = logging.getLogger(__name__)

STATE_MODIFICATION_METHODS = ["POST", "PUT", "DELETE", "PATCH"]


@dataclass
class Route:
    """
    Route objects are the building blocks of any scenario.
    You can think of it like a `given` statement that links a path and a handler.
    Routes can also be used to wait for them to be reached.

    Path matching is done by using starlette Routes.
    The Matcher type is nothing more than a starlette Route.
    """

    matcher: Matcher
    handler: Handler
    waiting = False

    @classmethod
    def build(cls, path: str, handler: Handler) -> "Route":
        """
        Build a new Route object.
        This method is exposed to hide the matcher implementation.
        """
        return cls(matcher=Matcher(path, lambda: None), handler=handler)

    def matches(self, path: str) -> bool:
        """
        Checks if a given path matches this route.
        :param path: the path to be matched
        :return: True if the path matches the route, False otherwise
        """
        if self.matcher:
            match, scope = self.matcher.matches({"type": "http", "path": path, "method": ""})
            return match != Match.NONE
        else:
            return True

    async def handle(self, *args, **kwargs):
        """
        Handles any request, passing the args and keyword-args to the stored handler.
        Additionally, notifies any Task waiting for this route to be reached.
        """
        log.debug(f"handle(): {self}")
        if self.waiting:
            await path_was_reached(self.matcher.path)

        return await self.handler(*args, **kwargs)

    async def was_reached(self, timeout: float):
        """
        Makes the current Task wait for the route to be reached.
        :param timeout: maximum time to wait for the route to be reached.
        """
        log.debug(f"was_reached(): {self}")
        self.waiting = True
        await wait_for_path(path=self.matcher.path, timeout=timeout)

    def __str__(self):
        return f"Route(path={self.matcher.path}, handler={self.handler}, waiting={self.waiting})"


class Routes(Dict[str, Route]):
    """
    Dict of routes having the path to be matched as a key and the Route as its value.
    You can think of this object as a cache of `givens` for a given scenario
    """

    def __init__(self, handlers: Dict[str, Handler]):
        super().__init__({path: Route.build(path, handler) for path, handler in handlers.items()})

    def find(
        self,
        path: str,
        method: Optional[str] = None,
        default: Optional[Callable[..., Awaitable[Any]]] = None,
    ):
        """
        This method will always return a Route. It can either:
        - return a matching route for the provided path
        - return a new route for any POST requests
        - return a new route if any default handler is provided
        - return a new route with a noop handler

        Route handlers will be overwritten if it has a noop handler and a default handler was provided.

        :param path: the path of the route
        :param method: an optional REST method (it also finds GRPC requests)
        :param default: an optional default handler if no route was found
        :return: an existing Route or a new one
        """
        log.debug(f"find(path={path}, method={method}, default={default})")
        matching_routes = [route for route in self.values() if route.matches(path)]
        if matching_routes:
            route = matching_routes[0]
            log.debug(f"find(): matching_route={route}")
        elif method in STATE_MODIFICATION_METHODS:
            # Return a mock response for any state modification request
            route = Route.build(path, WillReturn(JSONResponse({})))
            log.debug(f"find(): post_route={route}")
            self[path] = route
        elif default:
            route = Route.build(path, WillExecute(default))
            log.debug(f"find(): default_route={route}")
            self[path] = route
        else:
            route = Route.build(path, DoNothing())
            log.debug(f"find(): no_route={route}")
            self[path] = route

        if route.handler.noop() and method in STATE_MODIFICATION_METHODS:
            log.debug(f"find(): override_handler={method}")
            route.handler = WillReturn(JSONResponse({}))
        elif route.handler.noop() and default:
            log.debug(f"find(): override_handler={default}")
            route.handler = WillExecute(default)

        return route
