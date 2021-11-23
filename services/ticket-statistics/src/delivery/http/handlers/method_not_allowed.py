from flask import jsonify
from delivery.http.handlers.exceptions.project_exception import ProjectException
from delivery.http.handlers.error_handler import get_error_with_exception


def constructor_send_method_not_found(logger):
    def send_method_not_found(_):
        exception = ProjectException(tag='METHOD_NOT_FOUND')
        error = get_error_with_exception(exception)
        logger.info(exception.serialize)
        return jsonify(error), int(error['code'])
    return send_method_not_found
