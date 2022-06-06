from typing import Dict, Any

from asyncio import Task
from dataclasses import dataclass

LOGGING_CONTEXT_ATTR = "logging_context"


def get_logging_context() -> Dict[str, Any]:
    current_task = Task.current_task()
    return getattr(current_task, LOGGING_CONTEXT_ATTR, {})


def set_logging_context(**new_context):
    current_task = Task.current_task()
    if current_task:
        current_context = getattr(current_task, LOGGING_CONTEXT_ATTR, {})
        current_context = {**current_context, **new_context}
        setattr(current_task, LOGGING_CONTEXT_ATTR, current_context)


def remove_logging_context(*keys_to_be_removed):
    current_task = Task.current_task()
    if current_task:
        current_context = getattr(current_task, LOGGING_CONTEXT_ATTR, {})
        current_context = {key: value for key, value in current_context.items() if key not in keys_to_be_removed}
        setattr(current_task, LOGGING_CONTEXT_ATTR, current_context)


def logging_context(**context):
    return LocalLoggingContext(context=context)


@dataclass
class LocalLoggingContext:
    context: Dict[str, Any]

    def __enter__(self):
        set_logging_context(**self.context)

    def __exit__(self, exc_type, exc_value, traceback):
        remove_logging_context(*self.context.keys())
