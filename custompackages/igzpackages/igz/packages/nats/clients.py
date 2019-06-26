from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from igz.packages.eventbus.action import ActionWrapper
import logging
import sys
from tenacity import retry, wait_exponential, stop_after_delay
import shortuuid


class NatsStreamingClient:
    _nc = None
    _sc = None
    _subs = None
    _topic_action = None
    _config = None
    _uuid = None
    _client_id = ""
    _logger = None

    def __init__(self, config, client_id, logger=None):
        self._config = config.NATS_CONFIG
        self._uuid = shortuuid.uuid()[:8]
        self._client_id = client_id + self._uuid
        self._subs = list()
        self._topic_action = dict()
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
            # Use borrowed connection for NATS then mount NATS Streaming
            # client on top.
            self._nc = NATS()
            await self._nc.connect(servers=self._config["servers"], max_reconnect_attempts=self._config["reconnects"])
            # Start session with NATS Streaming cluster.
            self._sc = STAN()

            await self._sc.connect(self._config["cluster_name"], client_id=self._client_id,
                                   nats=self._nc, max_pub_acks_inflight=self._config["publisher"]
                                   ["max_pub_acks_inflight"])

        await connect_to_nats()

    async def publish(self, topic, message):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def publish(topic, message):

            if self._nc.is_connected:
                await self._sc.publish(topic, message.encode())
            else:
                await self.close_nats_connections()
                await self.connect_to_nats()
                await self._sc.publish(topic, message.encode())

        await publish(topic, message)

    async def _cb_with_ack_and_action(self, msg):
        self._logger.info(f'Message received from topic {msg.sub.subject} with sequence {msg.sequence}')
        event = msg.data
        if self._topic_action[msg.sub.subject] is None or type(
                self._topic_action[msg.sub.subject]) is not ActionWrapper:
            self._logger.error(f'No ActionWrapper defined for topic {msg.sub.subject}. Message not marked with ACK')
            return
        try:
            if self._topic_action[msg.sub.subject].is_async:
                await self._topic_action[msg.sub.subject].execute_stateful_action(event)
            else:
                self._topic_action[msg.sub.subject].execute_stateful_action(event)
            await self._sc.ack(msg)
        except Exception:
            self._logger.exception(f"NATS ClientException in {self._client_id} client happened")
            self._logger.exception(f"Error executing {self._topic_action[msg.sub.subject].execute_stateful_action} "f"")
            self._logger.exception("Won't ACK message")

    async def _cb_with_ack(self, msg):
        self._logger.info(f'Message received from topic {msg.sub.subject} with sequence {msg.sequence}')
        event = msg.data
        if self._topic_action[msg.sub.subject] is None:
            self._logger.error(f'No callback defined for topic {msg.sub.subject}. Message not marked with ACK')
            return
        try:
            self._topic_action[msg.sub.subject](event)
            await self._sc.ack(msg)
        except Exception:
            self._logger.exception(f"NATS ClientException in {self._client_id} client happened")
            self._logger.exception(f"Error executing {self._topic_action[msg.sub.subject]} function")

    async def subscribe_action(self, topic, action: ActionWrapper,
                               start_at='first', time=None, sequence=None, queue=None, durable_name=None):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def subscribe_action(topic, action: ActionWrapper,
                                   start_at='first', time=None, sequence=None, queue=None, durable_name=None):
            self._topic_action[topic] = action
            if self._nc.is_connected:
                sub = await self._sc.subscribe(topic,
                                               start_at=start_at,
                                               time=time,
                                               sequence=sequence,
                                               queue=queue,
                                               durable_name=durable_name,
                                               cb=self._cb_with_ack_and_action,
                                               manual_acks=True,
                                               max_inflight=self._config["subscriber"][
                                                   "max_inflight"],
                                               pending_limits=self._config["subscriber"][
                                                   "pending_limits"],

                                               ack_wait=99999)

            else:
                await self.close_nats_connections()
                await self.connect_to_nats()
                sub = await self._sc.subscribe(topic,
                                               start_at=start_at,
                                               time=time,
                                               sequence=sequence,
                                               queue=queue,
                                               durable_name=durable_name,
                                               cb=self._cb_with_ack_and_action,
                                               manual_acks=True,
                                               max_inflight=self._config["subscriber"][
                                                   "max_inflight"],
                                               pending_limits=self._config["subscriber"][
                                                   "pending_limits"],
                                               ack_wait=99999)
            self._subs.append(sub)

        await subscribe_action(topic, action, start_at, time, sequence, queue, durable_name)

    async def subscribe(self, topic, callback,
                        start_at='first', time=None, sequence=None, queue=None, durable_name=None):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'], min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def subscribe(topic, callback,
                            start_at='first', time=None, sequence=None, queue=None, durable_name=None):
            self._topic_action[topic] = callback
            if self._nc.is_connected:
                sub = await self._sc.subscribe(topic,
                                               start_at=start_at,
                                               time=time,
                                               sequence=sequence,
                                               queue=queue,
                                               durable_name=durable_name,
                                               cb=self._cb_with_ack,
                                               manual_acks=True,
                                               max_inflight=self._config["subscriber"]["max_inflight"],
                                               pending_limits=self._config["subscriber"]["pending_limits"],
                                               ack_wait=99999)
            else:
                await self.close_nats_connections()
                await self.connect_to_nats()
                sub = await self._sc.subscribe(topic,
                                               start_at=start_at,
                                               time=time,
                                               sequence=sequence,
                                               queue=queue,
                                               durable_name=durable_name,
                                               cb=self._cb_with_ack,
                                               manual_acks=True,
                                               max_inflight=self._config["subscriber"]["max_inflight"],
                                               pending_limits=self._config["subscriber"]["pending_limits"],
                                               ack_wait=99999)
            self._subs.append(sub)
        await subscribe(topic, callback, start_at, time, sequence, queue, durable_name)

    async def close_nats_connections(self):
        # Stop recieving messages
        for sub in self._subs:
            await sub.unsubscribe()
        # Close NATS Streaming session
        if self._nc.is_connected:
            await self._sc.close()
        # We are using a NATS borrowed connection so we need to close manually.
        if self._nc.is_closed is False:
            await self._nc.close()
