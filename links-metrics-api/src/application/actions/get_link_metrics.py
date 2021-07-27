from datetime import datetime, timedelta

import dateutil.parser

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

        start_time = int(dateutil.parser.isoparse(interval_start).timestamp() * 1000)
        json_res = GetLinkMetrics._get_empty_json_response()
        mongo_metrics = await self._mongo_client.get_from_interval(interval_start, interval_end)
        GetLinkMetrics._process_mongo_metrics(mongo_metrics, json_res, start_time)
        return json_res

    @staticmethod
    def _process_mongo_metrics(mongo_metrics, json_response, start_time):
        metrics_batches = [batch["metrics"] for batch in mongo_metrics]
        for batch in metrics_batches:
            for link in batch:
                GetLinkMetrics._create_or_update_link(json_response, link, start_time)

    @staticmethod
    def _get_empty_json_response():
        return {
            # This means nothing. Asked by O'Reilly to keep
            # the same format the are using.
            "jsonrpc": '2.0',
            # the "result" field is the only important one
            "result": [],
            # This means nothing. Asked by O'Reilly to keep
            # the same format the are using.
            "id": None
        }

    @staticmethod
    def _create_or_update_link(response, link, start_time):
        link_exists = GetLinkMetrics._link_exists(response, link)

        if not link_exists:
            link_record = GetLinkMetrics._create_link_record(link, start_time)
            response["result"].append(link_record)
        GetLinkMetrics._append_data_to_series(response, link)

    @staticmethod
    def _link_exists(response, link_data):
        exists = False
        for link in response["result"]:
            if GetLinkMetrics._is_same_link(link["link"], link_data["link"]):
                exists = True
        return exists

    @staticmethod
    def _append_data_to_series(response, link_data):
        for link in response["result"]:
            if GetLinkMetrics._is_same_link(link["link"], link_data["link"]):
                for serie in link["series"]:
                    metric_name = serie["metric"]
                    serie["data"].append(link_data[metric_name])
                    serie["total"] = serie["total"] + link_data[metric_name]
                    if serie["max"]:
                        serie["max"] = max(serie["max"], link_data[metric_name])
                    else:
                        serie["max"] = link_data[metric_name]
                    if serie["min"]:
                        serie["min"] = min(serie["min"], link_data[metric_name])
                    else:
                        serie["min"] = link_data[metric_name]

    @staticmethod
    def _is_same_link(link1, link2):
        same_enterprise_id = link1["enterpriseId"] == link2["enterpriseId"]
        same_edge_id = link1["edgeId"] == link2["edgeId"]
        same_link_id = link1["linkId"] == link2["linkId"]
        return same_link_id and same_edge_id and same_enterprise_id

    @staticmethod
    def _create_link_record(link, start_time):
        return {
            "series": GetLinkMetrics._create_series_array(start_time),
            "linkId": link["link"]["linkId"],
            "edgeId": link["link"]["edgeId"],
            "link": link["link"]

        }

    @staticmethod
    def _create_series_array(start_time):
        return [GetLinkMetrics._create_series_record(series_name, start_time)
                for series_name in METRICS_LIST
                ]

    @staticmethod
    def _create_series_record(name, start_time):
        return {
            "metric": name,
            "startTime": start_time,
            "tickInterval": 300000,
            "data": [],
            "total": 0,
            "min": None,
            "max": None
        }
