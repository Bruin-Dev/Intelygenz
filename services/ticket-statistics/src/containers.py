from adapters.containers import Adapters
from delivery.containers import Delivery
from dependency_injector import containers, providers
from usecases.containers import UseCases


class Application(containers.DeclarativeContainer):
    adapters = providers.Container(Adapters)

    use_cases = providers.Container(UseCases, adapters=adapters)

    delivery = providers.Container(Delivery, adapters=adapters, use_cases=use_cases)
