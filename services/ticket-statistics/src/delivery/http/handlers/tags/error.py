ERRORS = {
    'INTERNAL_ERROR': {
        'code': 500,
        'message': 'Internal error',
    },
    'NOT_FOUND': {
        'code': 404,
        'message': 'Not found',
    },
    'MISSING_DATES': {
        'code': 400,
        'message': "Missing 'start' or 'end' parameters",
    },
    'INVALID_DATES': {
        'code': 400,
        'message': 'Invalid dates, please specify a valid format',
    },
    'INVALID_DATE_RANGE': {
        'code': 400,
        'message': "Invalid date range, 'start' cannot be after 'end'",
    },
}
