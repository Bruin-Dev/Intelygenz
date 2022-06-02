from dependency_injector.wiring import Provide, inject
from usecases.containers import UseCases
from usecases.tickets import TicketUseCase


@inject
async def get_data(tickets_use_cases: TicketUseCase = Provide[UseCases.tickets_use_case]) -> None:
    await tickets_use_cases.get_data()
