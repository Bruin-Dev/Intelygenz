import asyncio
import types
from typing import Any, List
from unittest.mock import AsyncMock, Mock


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
        if not method.startswith("__")
        if method not in excluded_methods
        if type(getattr(instance, method)) in [types.MethodType, types.FunctionType]
    ]

    for method_name in wrappable_methods:
        method = getattr(instance, method_name)

        if asyncio.iscoroutinefunction(method):
            setattr(instance, method_name, AsyncMock(wraps=method))
        else:
            setattr(instance, method_name, Mock(wraps=method))
