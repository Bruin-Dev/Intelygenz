from application.clients.nats_streaming_client import NatsStreamingClient
from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient(config)
    await nats_s_client.connect_to_nats()
    await nats_s_client.publish_message("Some-topic", "Some message")
    await nats_s_client.publish_message("Some-topic", "Some message2")
    await nats_s_client.publish_message("Some-topic", "Some message3")
    await nats_s_client.register_consumer()
    print("Waiting 5 seconds to consume messages...")
    await aiosleep(5)
    await nats_s_client.close_nats_connections()


def velocloud_hello_world():
    import velocloud
    import os
    from velocloud.rest import ApiException
    client = velocloud.ApiClient(host=os.environ["VELOCLOUD_HOST"])
    client.authenticate(os.environ["VELOCLOUD_USER"], os.environ["VELOCLOUD_PASS"], operator=True)

    api = velocloud.AllApi(client)

    print("### GETTING AGGREGATE ENTERPRISES EDGES: THIS MEANS GETTING ALL WE NEED TO START  ###")
    body = {}
    try:
        res = api.monitoringGetAggregates(body=body)
        print(res)
    except ApiException as e:
        print(e)


if __name__ == '__main__':
    print("Bruin bridge starting...")
    velocloud_hello_world()
    # run()