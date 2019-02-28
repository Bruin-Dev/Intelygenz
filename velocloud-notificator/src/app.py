from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
import requests
import json


def print_callback(msg):
    # Slack Notificator
    print('Detected faulty edge. Taking notification actions...')
    web_hook_url = "https://hooks.slack.com/services/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"
    slack_msg = {'text': msg}
    # Include a try and except to check for a ConnectionError
    # so post wont try to send data to a failed link or failed connection
    # requests.post(web_hook_url, data=json.dumps(slack_msg))
    try:
        print(msg)
        requests.post(web_hook_url, data=json.dumps(slack_msg))
    except ConnectionError as e:
        print("Connection failed")
        print(e)


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient(config, "velocloud-notificator-subscriber")

    await nats_s_client.connect_to_nats()
    # actual code
    #############
    # await nats_s_client.subscribe(topic="edge.status.ko", callback=print_callback(slack_url=web_hook_url))
    # test scenarios
    #############
    await nats_s_client.publish("successful_slack", "Connection to slack was successful")
    await nats_s_client.subscribe(topic="successful_slack", callback=print_callback)
    # await nats_s_client.publish("Failed_slack", "Connection to slack was unsuccessful")
    # await nats_s_client.subscribe(topic="Failed_slack", callback=print_callback)
    delay = 10
    print(f'Waiting {delay} seconds to consume messages...')
    await aiosleep(delay)
    await nats_s_client.close_nats_connections()


if __name__ == '__main__':
    print("Velocloud notificator starting...")
    run()
