import asyncio
import logging
from typing import Any, Awaitable, Callable, Optional

from application.data.bruin import Document, Inventory
from application.data.bruin.ticket_basic import TicketBasic
from application.data.bruin.ticket_details import TicketDetails, TicketNote
from application.handler import Handler, WillReturnJSON
from application.route import Route, Routes
from dataclasses import dataclass, field
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger(__name__)


# These are the default routes for any scenario. It can be expected for this dict to grow on any iteration.
DEFAULT_ROUTES = {
    "/login/identity/connect/token": WillReturnJSON({"access_token": "token"}),
    "/api/Ticket/basic": WillReturnJSON(TicketBasic()),
    "/api/Ticket/{ticket_id}/notes/advanced": WillReturnJSON({"ticketNotes": []}),
    "/api/Ticket/{ticket_id}/details": WillReturnJSON(
        TicketDetails(ticketNotes=[TicketNote(serviceNumber=["VC05200011984"])])
    ),
    "/api/Inventory": WillReturnJSON(Inventory(documents=[Document()])),
    "/api/Email/{email_id}/link/ticket/{ticket_id}": WillReturnJSON({"success": "success"}),
    "/api/Email/status": WillReturnJSON({"success": "success"}),
}


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    reason: Optional[str] = None


@dataclass
class Scenario:
    """
    Scenario base class to be extended. It gives shorthand methods to build expressive scenarios.
    """

    name: str
    routes: Routes = field(default_factory=lambda: Routes(DEFAULT_ROUTES))

    async def run(self) -> ScenarioResult:
        """
        This is the main method to be overriden.
        Subclasses will fill it with their given, when and then statements.
        :return: the result of the scenario
        """
        pass

    async def handle_asgi(self, request: Request, resend: Callable[[Request], Awaitable[Response]]) -> Any:
        """
        Handles any starlette request.
        It will look for any route that matches the request path and invoke its handle method.
        The resend callable provided will be used as the default handler in case no route matched the request path.
        This will make any uncontrolled path to be resent to its original endpoint (if any)
        :param request: a REST request
        :param resend: a resend method to be used as the default handler
        :return: the request response (either mocked or proxied)
        """
        log.debug(f"handle_asgi(path={request.url.path}, method={request.method}, resend={resend}")
        route = self.routes.find(path=request.url.path, method=request.method, default=resend)
        log.debug(f"handle_asgi(): route={route}")
        return await route.handle(request)

    async def handle_grpc(self, path: str, request, context, resend: Callable[..., Awaitable[Any]]) -> Any:
        """
        Handles any GRPC request.
        It will look for any route that matches the request path and invoke its handle method.
        The resend callable provided will be used as the default handler in case no route matched the request path.
        This will make any uncontrolled path to be resent to its original endpoint (if any)
        :param path: a GRPC path
        :param request: a GRPC request
        :param context: a GRPC context
        :param resend: a resend method to be used as the default handler
        :return: the request response (either mocked or proxied)
        """
        log.debug(f"handle_grpc(path={path}, request={request}, resend={resend}")
        route = self.routes.find(path=path, default=resend)
        log.debug(f"handle_grpc(): route={route}")
        return await route.handle(request, context)

    def given(self, path: str, handler: Handler) -> Route:
        """
        Shorthand method to use in the scenario implementation.
        :param path: the path to be mocked or proxied
        :param handler: the handler for the path
        """
        log.debug(f"given(path={path}, handler={handler}")
        route = self.routes.find(path)
        route.handler = handler
        return route

    def route(self, path: str) -> Route:
        """
        Shorthand to find a route that matched the given path.
        If no route matches the ones that are defined, a default Route will be returned.
        :param path:
        :return:
        """
        return self.routes.find(path)

    def passed(self) -> ScenarioResult:
        """
        Shorthand to build a passed scenario result
        :return: a passed scenario result
        """
        return ScenarioResult(name=self.name, passed=True)

    def failed(self, reason: Optional[str] = None) -> ScenarioResult:
        """
        Shorthand to build a failed scenario result
        :return: a failed scenario result
        """
        return ScenarioResult(name=self.name, passed=False, reason=reason)

    async def check(self, *args: Awaitable) -> ScenarioResult:
        results = await asyncio.gather(*args, return_exceptions=True)
        failed_waits = [failed_wait for failed_wait in results if isinstance(failed_wait, Exception)]
        if failed_waits:
            return self.failed(reason=str(failed_waits))
        else:
            return self.passed()


# default scenario to be used when the server is idle and not executing any scenario
_no_scenario = Scenario(name="_no_scenario")
# global scenario that holds the current scenario being executed
_current_scenario: Scenario = _no_scenario


def get_current_scenario() -> Scenario:
    global _current_scenario
    return _current_scenario


def set_current_scenario(scenario: Scenario):
    global _current_scenario
    _current_scenario = scenario


def clear_current_scenario():
    global _current_scenario
    _current_scenario = _no_scenario
