import logging
import sys

from nats.aio.client import Client as NATS
from tenacity import retry, wait_exponential, stop_after_delay

from igz.packages.eventbus.action import ActionWrapper


class NATSClient:

    def __init__(self, config, logger=None):
        self._config = config.NATS_CONFIG
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
        async def publish(topic, message):

            if self._nc.is_connected:
                await self._nc.publish(topic, message.encode())
            else:
                await self.close_nats_connections()
                await self.connect_to_nats()
                await self._nc.publish(topic, message.encode())

        await publish(topic, message)

    async def rpc_request(self, topic, message, timeout=10):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def rpc_request(topic, message, timeout):
            if self._nc.is_connected:
                rpc_request = await self._nc.timed_request(topic, message.encode(), timeout)
                return json.loads(rpc_request.data)
            else:
                await self.close_nats_connections()
                await self.connect_to_nats()
                rpc_request = await self._nc.timed_request(topic, message.encode(), timeout)
                return json.loads(rpc_request.data)

        return await rpc_request(topic, message, timeout)

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
                # TODO: Don't do json.dump, just pass msg.data to the function
                await self._topic_action[msg.subject].execute_stateful_action(json.dumps(event))
            else:
                # TODO: Don't do json.dump, just pass msg.data to the function
                self._topic_action[msg.subject].execute_stateful_action(json.dumps(event))
        except Exception:
            self._logger.exception(f"NATS Client Exception in client happened")
            self._logger.exception(f"Error executing {self._topic_action[msg.subject].execute_stateful_action} "f"")
            self._logger.exception("Won't ACK message")

    async def subscribe_action(self, topic, action: ActionWrapper, queue=""):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def subscribe_action(topic, action: ActionWrapper, queue=""):
            self._topic_action[topic] = action
            if self._nc.is_connected:
                sub = await self._nc.subscribe(topic,
                                               queue=queue,
                                               is_async=True,
                                               cb=self._cb_with_ack_and_action,
                                               pending_msgs_limit=self._config["subscriber"][
                                                   "pending_limits"])

            else:
                await self.close_nats_connections()
                await self.connect_to_nats()
                sub = await self._nc.subscribe(topic,
                                               queue=queue,
                                               is_async=True,
                                               cb=self._cb_with_ack_and_action,
                                               pending_msgs_limit=self._config["subscriber"][
                                                   "pending_limits"])
            self._subs.append(sub)

        await subscribe_action(topic, action, queue)

    async def close_nats_connections(self):
        for sub in self._subs:
            await self._nc.drain(sub)
        if self._nc.is_closed is False:
            await self._nc.close()
