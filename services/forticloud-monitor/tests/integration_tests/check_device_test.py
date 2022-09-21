import pytest


@pytest.mark.integration
async def check_device_test(nats_client, settings, any_payload, bruin_server):
    # given
    # an offline device
    await bruin_server.mock_route(
        method="GET",
        path="/api/Device",
        return_value='{"status": "OFFLINE"}',
    )
    # an offline device
    create_ticket_route = await bruin_server.mock_route(
        method="POST",
        path="/api/Ticket/repair",
        return_value='{"assets":[{"ticketId":1}]}',
    )

    # when
    await nats_client.publish(settings.device_consumer_subject, any_payload)

    # then
    assert await create_ticket_route.was_reached(timeout=2)


@pytest.fixture()
def any_payload():
    return b'{"device_id":1,"device_network_id":2,"client_id":3,"service_number":4,"type":"AP"}'
