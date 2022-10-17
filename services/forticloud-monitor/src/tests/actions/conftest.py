from unittest.mock import AsyncMock, Mock

import pytest

from application.actions import CheckDevice
from application.repositories import BruinRepository, ForticloudRepository
from application.repositories.metrics_repository import MetricsRepository


@pytest.fixture
def any_check_device(any_offline_device, any_created_ticket, any_ticket):
    def builder(
        get_device: AsyncMock = AsyncMock(return_value=any_offline_device),
        post_repair_ticket: AsyncMock = AsyncMock(return_value=any_created_ticket),
        post_ticket_note: AsyncMock = AsyncMock(),
        find_open_automation_ticket_for: AsyncMock = AsyncMock(return_value=any_ticket),
        unpause_task: AsyncMock = AsyncMock(),
        resolve_task: AsyncMock = AsyncMock(),
        add_auto_resolved_task_metric: AsyncMock = AsyncMock(),
    ) -> CheckDevice:
        forticloud_repository = Mock(ForticloudRepository)
        forticloud_repository.get_device = get_device

        bruin_repository = Mock(BruinRepository)
        bruin_repository.post_repair_ticket = post_repair_ticket
        bruin_repository.post_ticket_note = post_ticket_note
        bruin_repository.find_open_automation_ticket_for = find_open_automation_ticket_for
        bruin_repository.unpause_task = unpause_task
        bruin_repository.resolve_task = resolve_task

        metrics_repository = Mock(MetricsRepository)
        metrics_repository.add_auto_resolved_task_metric = add_auto_resolved_task_metric

        check_device = CheckDevice(forticloud_repository, bruin_repository, metrics_repository)

        return check_device

    return builder
