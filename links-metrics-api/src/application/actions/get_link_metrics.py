METRICS_LIST = ['bytesRx', 'bytesTx', 'totalBytes', 'totalPackets', 'p1BytesRx', 'p1BytesTx', 'p1PacketsRx',
                'p1PacketsTx', 'p2BytesRx', 'p2BytesTx', 'p2PacketsRx', 'p2PacketsTx', 'p3BytesRx', 'p3BytesTx',
                'p3PacketsRx', 'p3PacketsTx', 'packetsRx', 'packetsTx', 'controlBytesRx', 'controlBytesTx',
                'controlPacketsRx', 'controlPacketsTx', 'bestJitterMsRx', 'bestJitterMsTx', 'bestLatencyMsRx',
                'bestLatencyMsTx', 'bestLossPctRx', 'bestLossPctTx', 'bpsOfBestPathRx', 'bpsOfBestPathTx',
                'signalStrength', 'scoreTx', 'scoreRx']


class GetLinkMetrics:
    def __init__(self, logger, config, mongo_client):
        self._logger = logger
        self._config = config
        self._mongo_client = mongo_client

    async def get_links_metrics(self, start_date, end_date):
        interval_start = start_date
        interval_end = end_date
        mongo_metrics = await self._mongo_client.get_from_interval(interval_start, interval_end)
        return mongo_metrics
