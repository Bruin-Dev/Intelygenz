from dependency_injector.wiring import inject, Provide
from usecases.statistics import StatisticsUseCase

from usecases.containers import UseCases
import datetime


@inject
def get_blueprint(statistics_use_case: StatisticsUseCase = Provide[UseCases.statistics_use_case]):
    from flask import Response
    from flask_smorest import Blueprint
    from delivery.http.handlers import response_handler
    from delivery.http.handlers.tags.response import RESPONSES
    from flask import request
    from delivery.http.handlers.exceptions.project_exception import ProjectException

    endpoint = '/statistics'
    name = 'statistics'

    blueprint = Blueprint(name, __name__, template_folder='blueprints')

    @blueprint.route(endpoint, methods=['GET'], strict_slashes=False)
    def get_statistics(**kwargs) -> Response:
        """Get statistics data between dates"""
        try:
            start = to_date(request.args.get('start'))
            end = to_date(request.args.get('end'))

            statistics_use_case.calculate_statistics(start=start, end=end)

            return response_handler.response(tag=RESPONSES['RESOURCE_FOUND'])
        except ValueError:
            raise ProjectException('DATES_FORMAT')

    def to_date(date_string):
        try:
            return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError('{} is not valid date in the format YYYY-MM-DD'.format(date_string))

    return blueprint
