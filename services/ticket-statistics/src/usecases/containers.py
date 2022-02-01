from dependency_injector import containers, providers
from usecases.statistics import StatisticsUseCase
from adapters.logger.logger import get_logger
from adapters.config.settings import get_config


class UseCases(containers.DeclarativeContainer):
    adapters = providers.DependenciesContainer()
    config = providers.Singleton(get_config)
    tickets_repository = adapters.tickets_repository
    metrics_repository = adapters.metrics_repository
    logger = providers.Singleton(get_logger, config=config)

    statistics_use_case: StatisticsUseCase = providers.Singleton(
        StatisticsUseCase,
        tickets_repository=tickets_repository,
        metrics_repository=metrics_repository,
        logger=logger
    )
