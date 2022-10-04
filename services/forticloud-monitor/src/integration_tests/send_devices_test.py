import pytest


@pytest.mark.integration
async def new_ap_ticket_test(nats_client, config, bruin_server, bruin_login, forticloud_server, forticloud_login):
    # given
    payload = b'{"device_id":1,"device_network_id":2,"client_id":3,"service_number":4}'
    # a succesful login
    await bruin_login()
    await forticloud_login()
    # an offline AP
    await forticloud_server.mock_route(
        method="GET",
        path="/networks/2/fap/access_points/1",
        return_value='{"connection_state": "disconnected"}',
    )
    # a new created ticket
    await bruin_server.mock_route(
        method="POST",
        path="/api/Ticket/repair",
        return_value='{"assets":[{"ticketId":1}]}',
    )
    # a note posted
    post_note = await bruin_server.mock_route(
        method="POST",
        path="/api/Ticket/1/notes",
        return_value="",
    )

    # when
    await nats_client.publish(config.ap_consumer_subject, payload)

    # then
    assert await post_note.was_reached(timeout=2)


@pytest.mark.integration
async def reopen_switch_ticket_test(
    nats_client, config, bruin_server, bruin_login, forticloud_server, forticloud_login
):
    # given
    payload = b'{"device_id":1,"device_network_id":2,"client_id":3,"service_number":4}'
    # a succesful login
    await bruin_login()
    await forticloud_login()
    # an offline switch
    await forticloud_server.mock_route(
        method="GET",
        path="/networks/2/fsw/switch/switches/1",
        return_value='{"status": "offline"}',
    )
    await bruin_server.mock_route(
        method="POST",
        path="/api/Ticket/repair",
        return_value='{"assets":[{"ticketId":1}]}',
    )
    post_note = await bruin_server.mock_route(
        method="POST",
        path="/api/Ticket/1/notes",
        return_value="",
    )

    # when
    await nats_client.publish(config.switch_consumer_subject, payload)

    # then
    assert await post_note.was_reached(timeout=2)
