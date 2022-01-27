from dependency_injector import containers, providers
from usecases.tickets import TicketUseCase
from adapters.logger.logger import get_logger
from adapters.config.settings import get_config


class UseCases(containers.DeclarativeContainer):
    adapters = providers.DependenciesContainer()
    config = providers.Singleton(get_config)
    bruin_repository = adapters.bruin_repository
    tickets_repository = adapters.tickets_repository
    logger = providers.Singleton(get_logger, config=config)

    tickets_use_case: TicketUseCase = providers.Singleton(
        TicketUseCase,
        bruin_repository=bruin_repository,
        tickets_repository=tickets_repository,
        config=config,
        logger=logger
    )
