import asyncio
import types
from datetime import datetime
from typing import Any
from typing import List
from unittest.mock import Mock

from asynctest import CoroutineMock
from pytz import timezone

from fixtures._constants import BRUIN_API_TIMEZONE
from fixtures._constants import VELOCLOUD_API_TIMEZONE


# Use this sentinel as a default value for arguments of fixtures' factories, so users can pass None
# as a valid value for any field
_undefined = object()


def bruinize_date(dt: datetime) -> str:
    """
    Transforms a datetime into a string compliant with format (ISO 8601) and timezone used by Bruin API.
    The datetime object must be timezone aware, otherwise this helper might return unexpected results. Avoid using
    functions like datetime.utcnow()

    The result should look similar to this: 2020-09-08T19:40:12.247-04:00
    """
    date = dt.astimezone(timezone(BRUIN_API_TIMEZONE))

    date_str = date.isoformat()
    fragments = date_str.split('-')
    fragments[-2] = fragments[-2][:-3]  # Keep 3 out of 6 millisecond digits

    return '-'.join(fragments)


def wrap_all_methods(instance: Any, *, excluded_methods: List[str] = None):
    """
    This helper turns all methods (both static and non-static) of a given instance into mocks so they are
    easier to analyze while testing.
    """

    if excluded_methods is None:
        excluded_methods = []

    wrappable_methods = [
        method
        for method in dir(instance)
        if not method.startswith('__')
        if method not in excluded_methods
        if type(getattr(instance, method)) in [types.MethodType, types.FunctionType]
    ]

    for method_name in wrappable_methods:
        method = getattr(instance, method_name)

        if asyncio.iscoroutinefunction(method):
            setattr(instance, method_name, CoroutineMock(wraps=method))
        else:
            setattr(instance, method_name, Mock(wraps=method))
