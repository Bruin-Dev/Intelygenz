import asyncio
import types
from datetime import datetime
from typing import Any
from typing import List
from unittest.mock import Mock

from asynctest import CoroutineMock
from pytz import timezone

from tests.fixtures._constants import BRUIN_API_TIMEZONE

# Use this sentinel as a default value for arguments of fixtures' factories, so users can pass None
# as a valid value for any field
_undefined = object()


def bruinize_date(dt: datetime) -> str:
    date = dt.astimezone(timezone(BRUIN_API_TIMEZONE))

    date_str = date.isoformat()
    fragments = date_str.split('-')
    fragments[-2] = fragments[-2][:-3]  # Keep 3 out of 6 millisecond digits

    return '-'.join(fragments)


def wrap_all_methods(instance: Any, *, excluded_methods: List[str] = None):
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
