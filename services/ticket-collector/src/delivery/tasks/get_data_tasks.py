from dependency_injector.wiring import inject, Provide
from usecases.tickets import TicketUseCase
from usecases.containers import UseCases


@inject
async def get_data(tickets_use_cases: TicketUseCase = Provide[UseCases.tickets_use_case]) -> None:
    await tickets_use_cases.get_data()
