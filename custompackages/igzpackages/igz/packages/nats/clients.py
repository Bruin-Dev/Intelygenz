import json
import logging
import sys

from nats.aio.client import Client as NATS
from tenacity import retry, wait_exponential, stop_after_delay

from igz.packages.eventbus.action import ActionWrapper


class NATSClient:

    def __init__(self, config, messages_storage_manager, logger=None):
        self._config = config.NATS_CONFIG
        self._messages_storage_manager = messages_storage_manager
        self._topic_action = dict()
        self._subs = list()
        if logger is None:
            logger = logging.getLogger('nats')
            logger.setLevel(logging.DEBUG)
            log_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s: %(module)s: %(levelname)s: %(message)s')
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        self._logger = logger

    async def connect_to_nats(self):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def connect_to_nats():
            self._nc = NATS()
            await self._nc.connect(servers=self._config["servers"], max_reconnect_attempts=self._config["reconnects"])

        await connect_to_nats()

    async def publish(self, topic, message):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def publish():
            if not self._nc.is_connected:
                await self.close_nats_connections()
                await self.connect_to_nats()

            await self._nc.publish(topic, message.encode())

        await publish()

    async def rpc_request(self, topic, message, timeout=10):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def rpc_request():
            if not self._nc.is_connected:
                await self.close_nats_connections()
                await self.connect_to_nats()

            rpc_request = await self._nc.timed_request(topic, message.encode(), timeout)
            return json.loads(rpc_request.data)

        return await rpc_request()

    async def _cb_with_ack_and_action(self, msg):
        self._logger.info(f'Message received from topic {msg.subject}')
        event = json.loads(msg.data)
        event["response_topic"] = msg.reply
        if self._topic_action[msg.subject] is None or type(
                self._topic_action[msg.subject]) is not ActionWrapper:
            self._logger.error(f'No ActionWrapper defined for topic {msg.subject}. Message not marked with ACK')
            return
        try:
            if self._topic_action[msg.subject].is_async:
                await self._topic_action[msg.subject].execute_stateful_action(event)
            else:
                self._topic_action[msg.subject].execute_stateful_action(event)
        except Exception:
            self._logger.exception(f"NATS Client Exception in client happened")
            self._logger.exception(f"Error executing {self._topic_action[msg.subject].execute_stateful_action} "f"")
            self._logger.exception("Won't ACK message")

    async def subscribe_action(self, topic, action: ActionWrapper, queue=""):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def subscribe_action():
            self._topic_action[topic] = action

            if not self._nc.is_connected:
                await self.close_nats_connections()
                await self.connect_to_nats()

            sub = await self._nc.subscribe(topic,
                                           queue=queue,
                                           is_async=True,
                                           cb=self._cb_with_ack_and_action,
                                           pending_msgs_limit=self._config["subscriber"][
                                               "pending_limits"])
            self._subs.append(sub)

        await subscribe_action()

    async def close_nats_connections(self):
        for sub in self._subs:
            await self._nc.drain(sub)
        if self._nc.is_closed is False:
            await self._nc.close()
