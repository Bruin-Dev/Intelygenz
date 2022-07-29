import json
import logging
import sys

from igz.packages.eventbus.action import ActionWrapper
from nats.aio.client import Client as NATS
from tenacity import retry, stop_after_delay, wait_exponential


class NATSClient:
    def __init__(self, config, logger=None):
        self._config = config.NATS_CONFIG
        self._topic_action = dict()
        self._subs = list()
        if logger is None:
            logger = logging.getLogger("nats")
            logger.setLevel(logging.DEBUG)
            log_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s: %(module)s: %(levelname)s: %(message)s")
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        self._logger = logger

    async def connect_to_nats(self):
        @retry(
            wait=wait_exponential(multiplier=self._config["multiplier"], min=self._config["min"]),
            stop=stop_after_delay(self._config["stop_delay"]),
        )
        async def connect_to_nats():
            self._nc = NATS()

            self._logger.info(f"Connecting client to NATS servers: {self._config['servers']}...")
            await self._nc.connect(servers=self._config["servers"], max_reconnect_attempts=self._config["reconnects"])
            self._logger.info(f"Connected to NATS servers successfully")

        await connect_to_nats()

    async def publish(self, topic, message):
        @retry(
            wait=wait_exponential(multiplier=self._config["multiplier"], min=self._config["min"]),
            stop=stop_after_delay(self._config["stop_delay"]),
        )
        async def publish():
            self._logger.info(f"Publishing message to subject {topic}...")

            if not self._nc.is_connected:
                self._logger.warning(f"NATS client is disconnected from the NATS server. Resetting connection...")
                await self.close_nats_connections()
                await self.connect_to_nats()

            await self._nc.publish(topic, message.encode())
            self._logger.info(f"Message published to subject {topic} successfully")

        await publish()

    async def rpc_request(self, topic, message, timeout=10):
        @retry(
            wait=wait_exponential(multiplier=self._config["multiplier"], min=self._config["min"]),
            stop=stop_after_delay(self._config["stop_delay"]),
        )
        async def rpc_request():
            self._logger.info(f"Publishing request message to subject {topic}...")

            if not self._nc.is_connected:
                self._logger.warning(f"NATS client is disconnected from the NATS server. Resetting connection...")
                await self.close_nats_connections()
                await self.connect_to_nats()

            rpc_request = await self._nc.timed_request(topic, message.encode(), timeout)
            self._logger.info(f"Got response message from subject {topic}")

            return json.loads(rpc_request.data)

        return await rpc_request()

    async def _cb_with_action(self, msg):
        msg_subject = msg.subject

        self._logger.info(f"Message received from topic {msg_subject}")
        if self._topic_action[msg_subject] is None or not isinstance(self._topic_action[msg_subject], ActionWrapper):
            self._logger.error(f"No ActionWrapper defined for topic {msg_subject}.")
            return

        event = json.loads(msg.data)
        event["response_topic"] = msg.reply

        try:
            if self._topic_action[msg_subject].is_async:
                await self._topic_action[msg_subject].execute_stateful_action(event)
            else:
                self._topic_action[msg_subject].execute_stateful_action(event)
        except Exception:
            self._logger.exception(
                "NATS Client Exception in client happened. "
                f"Error executing action {self._topic_action[msg_subject].target_function} "
                f"from {type(self._topic_action[msg_subject].state_instance).__name__} instance."
            )

    async def subscribe_action(self, topic, action: ActionWrapper, queue=""):
        @retry(
            wait=wait_exponential(multiplier=self._config["multiplier"], min=self._config["min"]),
            stop=stop_after_delay(self._config["stop_delay"]),
        )
        async def subscribe_action():
            self._logger.info(
                f"Subscribing action {type(action.state_instance).__name__} to subject {topic} under NATS queue "
                f"{queue}..."
            )
            self._topic_action[topic] = action

            if not self._nc.is_connected:
                self._logger.warning(f"NATS client is disconnected from the NATS server. Resetting connection...")
                await self.close_nats_connections()
                await self.connect_to_nats()

            sub = await self._nc.subscribe(
                topic,
                queue=queue,
                is_async=True,
                cb=self._cb_with_action,
                pending_msgs_limit=self._config["subscriber"]["pending_limits"],
            )
            self._logger.info(
                f"Action {type(action.state_instance).__name__} subscribed to subject {topic} successfully"
            )

            self._subs.append(sub)

        await subscribe_action()

    async def close_nats_connections(self):
        self._logger.info("Draining connections...")
        for sub in self._subs:
            await self._nc.drain(sub)
        self._logger.info("Connections drained")

        if self._nc.is_closed is False:
            self._logger.info("Closing connection...")
            await self._nc.close()
            self._logger.info("Connection closed")
