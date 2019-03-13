import logging
import sys
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from igz.packages.eventbus.action import ActionWrapper
from igz.packages.Logger.logger_client import LoggerClient


class NatsStreamingClient:
    _nc = None
    _sc = None
    _subs = None
    _topic_action = None
    _config = None
    _client_id = ""
    info_log = LoggerClient().create_logger('nats-client-OK', sys.stdout, logging.INFO)
    error_log = LoggerClient().create_logger('nats-client-KO', sys.stderr, logging.ERROR)

    def __init__(self, config, client_id):
        self._config = config.NATS_CONFIG
        self._client_id = client_id
        self._subs = list()
        self._topic_action = dict()

    async def connect_to_nats(self):
        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self._nc = NATS()
        await self._nc.connect(servers=self._config["servers"])
        # Start session with NATS Streaming cluster.
        self._sc = STAN()
        await self._sc.connect(self._config["cluster_name"], client_id=self._client_id,
                               nats=self._nc, max_pub_acks_inflight=self._config["publisher"]["max_pub_acks_inflight"])

    async def publish(self, topic, message):
        await self._sc.publish(topic, message.encode())

    async def _cb_with_ack_and_action(self, msg):
        self.info_log.info(f'Message received from topic {msg.sub.subject} with sequence {msg.sequence}')
        event = msg.data
        if self._topic_action[msg.sub.subject] is None or type(
                self._topic_action[msg.sub.subject]) is not ActionWrapper:
            self.error_log.error(f'No ActionWrapper defined for topic {msg.sub.subject}. Message not marked with ACK')
            return
        try:
            if self._topic_action[msg.sub.subject].is_async:
                await self._topic_action[msg.sub.subject].execute_stateful_action(event)
            else:
                self._topic_action[msg.sub.subject].execute_stateful_action(event)
            await self._sc.ack(msg)
        except Exception:
            self.error_log.error(f"NATS ClientException in {self._client_id} client happened")
            self.error_log.error(f"Error executing {self._topic_action[msg.sub.subject].execute_stateful_action} "
                                 f"")
            self.error_log.error("Won't ACK message")

    async def _cb_with_ack(self, msg):
        self.info_log.info(f'Message received from topic {msg.sub.subject} with sequence {msg.sequence}')
        event = msg.data
        if self._topic_action[msg.sub.subject] is None:
            self.error_log.error(f'No callback defined for topic {msg.sub.subject}. Message not marked with ACK')
            return
        try:
            self._topic_action[msg.sub.subject](event)
            await self._sc.ack(msg)
        except Exception:
            self.error_log.error(f"NATS ClientException in {self._client_id} client happened")
            self.error_log.error(f"Error executing {self._topic_action[msg.sub.subject]} function")

    async def subscribe_action(self, topic, action: ActionWrapper,
                               start_at='first', time=None, sequence=None, queue=None, durable_name=None):
        self._topic_action[topic] = action
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
                                           "pending_limits"])
        self._subs.append(sub)

    async def subscribe(self, topic, callback,
                        start_at='first', time=None, sequence=None, queue=None, durable_name=None):
        self._topic_action[topic] = callback
        sub = await self._sc.subscribe(topic,
                                       start_at=start_at,
                                       time=time,
                                       sequence=sequence,
                                       queue=queue,
                                       durable_name=durable_name,
                                       cb=self._cb_with_ack,
                                       manual_acks=True,
                                       max_inflight=self._config["subscriber"]["max_inflight"],
                                       pending_limits=self._config["subscriber"]["pending_limits"])
        self._subs.append(sub)

    async def close_nats_connections(self):
        # Stop recieving messages
        for sub in self._subs:
            await sub.unsubscribe()
        # Close NATS Streaming session
        await self._sc.close()
        # We are using a NATS borrowed connection so we need to close manually.
        await self._nc.close()
