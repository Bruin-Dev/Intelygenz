import asyncio
import logging
from asyncio import Condition
from typing import Any, Awaitable, Callable, Dict, Optional

from application.handler import DoNothing, Handler, WillExecute, WillReturn
from dataclasses import dataclass, field
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Match
from starlette.routing import Route as Matcher

log = logging.getLogger(__name__)


@dataclass
class Route:
    matcher: Matcher
    handler: Handler
    waiting = False

    @classmethod
    def build(cls, path: str, handler: Handler):
        return cls(matcher=Matcher(path, lambda: None), handler=handler)

    def matches(self, path: str):
        if self.matcher:
            match, scope = self.matcher.matches({"type": "http", "path": path, "method": ""})
            return match != Match.NONE
        else:
            return True

    async def handle(self, *args, **kwargs):
        log.debug(f"handle(): {self}")
        if self.waiting:
            await route_reached(self.matcher.path)

        return await self.handler(*args, **kwargs)

    async def was_reached(self, timeout: float):
        log.info(f"waiting for {self.matcher.path}")
        self.waiting = True
        await for_route(path=self.matcher.path, timeout=timeout)

    def __str__(self):
        return f"Route(path={self.matcher.path}, handler={self.handler}, waiting={self.waiting})"


class Routes(Dict[str, Route]):
    def __init__(self, handlers: Dict[str, Handler]):
        super().__init__({path: Route.build(path, handler) for path, handler in handlers.items()})

    def find(
        self,
        path: str,
        method: Optional[str] = None,
        default: Optional[Callable[..., Awaitable[Any]]] = None,
    ):
        log.debug(f"find(path={path}, method={method}, default={default})")
        matching_routes = [route for route in self.values() if route.matches(path)]
        if matching_routes:
            route = matching_routes[0]
            log.debug(f"find(): matching_route={route}")
        elif method == "POST":
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

        if route.handler.noop() and default:
            log.debug(f"find(): override_handler={default}")
            route.handler = WillExecute(default)

        return route


# @dataclass
# class Route:
#     path: str
#     route: StarletteRoute = field(init=False)
#     waiting_call = False
#
#     def __post_init__(self):
#         self.route = StarletteRoute(self.path, lambda: None)
#
#     def __hash__(self):
#         return hash(self.path)
#
#     def __eq__(self, other: Route):
#         return self.path == other.path
#
#     def matches(self, path: str):
#         match, scope = self.route.matches({"type": "http", "path": path, "method": ""})
#         return match != Match.NONE
#
#     async def was_reached(self):
#         self.waiting_call = True
#         async with route_waiting:
#             try:
#                 log.info(f"route={self}, waiting_call={self.waiting_call}")
#                 await asyncio.wait_for(route_waiting.wait(), timeout=10.0)
#             except asyncio.exceptions.TimeoutError as e:
#                 raise TimeoutError from e


DEFAULT_ROUTES = {
    "/login/identity/connect/token": WillReturn(JSONResponse({"access_token": "token"})),
    "/api/Ticket/basic": WillReturn(JSONResponse({"responses": [], "total": 0})),
}


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    reason: Optional[str] = None


@dataclass
class Scenario:
    name: str
    routes: Routes = field(default_factory=lambda: Routes(DEFAULT_ROUTES))
    # route_handlers: Dict[str, Path] = field(default_factory=lambda: DEFAULT_PATHS)
    # waiting_route_condition: Optional[Route] = None

    async def run(self) -> ScenarioResult:
        pass

    async def handle_asgi(self, request: Request, resend: Callable[[Request], Awaitable[Response]]) -> Any:
        log.debug(f"handle_asgi(path={request.url.path}, method={request.method}, resend={resend}")
        route = self.routes.find(path=request.url.path, method=request.method, default=resend)
        log.debug(f"handle_asgi(): route={route}")
        return await route.handle(request)

    async def handle_grpc(self, path: str, request, context, resend: Callable[..., Awaitable[Any]]) -> Any:
        log.debug(f"handle_grpc(path={path}, request={request}, resend={resend}")
        route = self.routes.find(path=path, default=resend)
        log.debug(f"handle_grpc(): route={route}")
        return await route.handle(request, context)

    def given(self, path: str, handler: Handler):
        log.debug(f"given(path={path}, handler={handler}")
        route = self.routes.find(path)
        route.handler = handler

    def route(self, path: str) -> Route:
        return self.routes.find(path)

    # def path(
    #     self,
    #     path: str,
    #     default: Optional[Callable[..., Awaitable[Any]]] = None,
    #     method: Optional[str] = None,
    # ) -> (Route, Optional[Handler]):
    #     route = Route(path)
    #     matching_handlers = [handler for route, handler in self.route_handlers.items() if route.matches(path)]
    #     if matching_handlers:
    #         handler = matching_handlers[0]
    #     elif method == "POST":
    #         handler = Handler(return_value=JSONResponse({}))
    #         self.route_handlers[route] = handler
    #     elif default:
    #         handler = Handler(side_effect=default)
    #         self.route_handlers[route] = handler
    #     else:
    #         handler = None
    #         self.route_handlers[route] = handler
    #
    #     return route, handler
    #
    # def route(
    #     self,
    #     path: str,
    #     default: Optional[Callable[..., Awaitable[Any]]] = None,
    #     method: Optional[str] = None,
    # ):
    #     return self.path(path, default, method)[0]

    # def handler(
    #     self,
    #     path: str,
    #     default: Optional[Callable[..., Awaitable[Any]]] = None,
    #     method: Optional[str] = None,
    # ):
    #     return self.path(path, default, method)[1]

    def passed(self) -> ScenarioResult:
        return ScenarioResult(name=self.name, passed=True)

    def failed(self, reason: Optional[str] = None) -> ScenarioResult:
        return ScenarioResult(name=self.name, passed=False, reason=reason)


no_scenario = Scenario(name="no_scenario")
current_scenario: Scenario = no_scenario


def get_current_scenario() -> Scenario:
    return current_scenario


def set_current_scenario(scenario: Scenario):
    global current_scenario
    current_scenario = scenario


def clear_current_scenario():
    global current_scenario
    current_scenario = no_scenario


conditions: Dict[str, Condition] = {}


async def for_route(path: str, timeout: float):
    log.debug(f"for_route(path={path}, timeout={timeout})")
    global conditions
    condition = asyncio.Condition()
    conditions[path] = condition
    async with condition:
        try:
            log.debug(f"for_route(): wait_for={condition}")
            await asyncio.wait_for(condition.wait(), timeout)
        except asyncio.exceptions.TimeoutError:
            raise TimeoutError(f"Timed out waiting for {path}")


async def route_reached(path: str):
    log.debug(f"route_reached(path={path})")
    global conditions
    if path in conditions:
        condition = conditions[path]
        async with condition:
            log.debug(f"route_reached(): notifying condition={condition}")
            condition.notify_all()
