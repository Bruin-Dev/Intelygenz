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
    def get_statistics() -> Response:
        """Get statistics data between dates"""
        start = request.args.get('start')
        end = request.args.get('end')

        if not start or not end:
            raise ProjectException('MISSING_DATES')

        try:
            start_date = to_date(start)
            end_date = to_date(end)
        except ValueError:
            raise ProjectException('INVALID_DATES')

        statistics = statistics_use_case.calculate_statistics(start=start_date, end=end_date)

        return response_handler.response(tag=RESPONSES['RESOURCE_FOUND'], data=statistics)

    def to_date(date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m-%d")

    return blueprint
