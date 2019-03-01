from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
import requests
import json


def print_callback(msg):
    print('Detected faulty edge. Taking notification actions...')
    web_hook_url = 'https://hooks.slack.com/services/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'
    header = 'https://'
    # Formats the msg to be dumped by json
    slack_msg = {'text': str(msg)}
    # Looks for header inside web_hook_url inorder to determine whether
    # or not its a valid url
    if header in web_hook_url:
        response = requests.post(web_hook_url, data=json.dumps(slack_msg))
    else:
        print("Invalid URL")

    # if an error arises prints out the status code
    if response.status_code != 200:
        print('HTTP error', response.status_code)
    else:
        print(str(msg))


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient(config, "velocloud-notificator-subscriber")
    await nats_s_client.connect_to_nats()
    await nats_s_client.subscribe(topic="edge.status.ko", callback=print_callback, durable_name="name", queue="queue",
                                  start_at='first')
    delay = 10
    print(f'Waiting {delay} seconds to consume messages...')
    await aiosleep(delay)
    await nats_s_client.close_nats_connections()


if __name__ == '__main__':
    print("Velocloud notificator starting...")
    run()
