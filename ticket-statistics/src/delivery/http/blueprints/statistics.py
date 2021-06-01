from dependency_injector.wiring import inject, Provide
from usecases.containers import UseCases
from usecases.statistics import StatisticsUseCase


@inject
def get_blueprint(statistics_use_case: StatisticsUseCase = Provide[UseCases.statistics_use_case]):
    from flask import Response
    from flask_smorest import Blueprint
    from delivery.http.handlers import response_handler
    from delivery.http.handlers.tags.response import RESPONSES

    endpoint = '/statistics'
    name = 'statistics'

    blueprint = Blueprint(name, __name__, template_folder='blueprints')

    @blueprint.route(endpoint, methods=['GET'], strict_slashes=False)
    def get_statistics(**kwargs) -> Response:
        """Get statistics data between dates"""
        return response_handler.response(tag=RESPONSES['RESOURCE_FOUND'])

    return blueprint
