
from __future__ import print_function

from uuid import uuid4

import os
from asgiref.sync import async_to_sync
import velocloud
from velocloud.rest import ApiException

# If SSL verification disabled (e.g. in a development environment)
import urllib3

urllib3.disable_warnings()
velocloud.configuration.verify_ssl = False

client = velocloud.ApiClient(host=os.environ["VELOCLOUD_HOST"])
client.authenticate(os.environ["VELOCLOUD_USER"], os.environ["VELOCLOUD_PASS"], operator=True)

api = velocloud.AllApi(client)

UNIQ = str(uuid4())


print("### GETTING AGGREGATE ENTERPRISES EDGES: THIS MEANS GETTING ALL WE NEED TO START  ###")
body = {}
try:
    res = api.monitoringGetAggregates(body=body)
    print(res)
except ApiException as e:
    print(e)

print("### GETTING ALL ENTERPRISE EDGES BY ID: MetTel_Test ###")
body = {"enterpriseId": 1}
try:
    res = api.enterpriseGetEnterpriseEdges(body=body)
    print(res)
except ApiException as e:
    print(e)


print("### GETTING EDGE BY ID AND ENTERPRISE ID. MetTel_Test - Digi_Test ###")
body = {"id": 3987, "enterpriseId": 1}
try:
    res = api.edgeGetEdge(body=body)
    print(res)
except ApiException as e:
    print(e)


print("### GETTING EDGE LINK METRICS. MetTel_Test - Digi_Test - BACKDOOR TO GET LINK STATUS BY EDGE ID###")
# The id is the Edge one
body = {"enterpriseId": 1, "id": 3987}
try:
    res = api.metricsGetEdgeLinkMetrics(body=body)
    print(res)
except ApiException as e:
    print(e)


# FUNCTIONS NOT WORKING
# ===================================
#
# print("### TRY - GETTING META FROM A PATH ###")
# try:
#     res = api.meta(apiPath="/rest/configuration/getConfiguration")
#     print(res)
# except ApiException as e:
#     print(e)
#
# print("### TRY - GETTING LINK STATUS BY EDGE ID. MetTel_Test - Digi_Test. ###")
# body = {"startTime": "2018-02-22T13:17:14.137Z", "edgeId": 3987}
# try:
#     res = api.linkQualityEventGetLinkQualityEvents(body=body)
#     print(res)
# except ApiException as e:
#     print(e)

# ===================================


# REAL DATA QUERIES FROM SIGNET GROUP
# ===================================


# print("### GETTING ALL EVENTS BY ENTERPRISE ID: SIGNET ###")
# # Accepts filters and pagination
#
# # {"host": "mettel.velocloud.net", "enterprise_id": 137, "edge_id": 1602}
# body = {"enterpriseId": 137, "edgeId": 1602,  "interval": {
#     "end": datetime.now(utc),
#     "start": (datetime.now(utc)-timedelta(hours=168))}}
# try:
#     res = api.eventGetEnterpriseEvents(body=body)
#     print(res)
# except ApiException as e:
#     print(e)


# print("### GETTING EDGE BY ID AND ENTERPRISE ID. SIGNET ###")
# body = {"id": 3196, "enterpriseId": 2}
# try:
#     res = api.edgeGetEdge(body=body)
#     print(res)
# except ApiException as e:
#     print(e)

# ===================================


# BIG QUERIES
# ===================================


# LARGE BUT NICE OUTPUT VERY DETAILED

# print("### GETTING ALL EVENTS BY ENTERPRISE ID: MetTel_Test  ###")
# # Accepts filters, can figure out pagination
# body = {"enterpriseId": 2, "limit": 1}
# try:
#     res = api.eventGetEnterpriseEvents(body=body)
#     print(res)
# except ApiException as e:
#     print(e)

# print("### GETTING ENTERPRISES EDGE LINK STATUS: MetTel_Test. THIS MEANS GETTING ALL. ACCEPTS ARRAY OF IDS ###")
# body = {"enterprises": [1]}
# try:
#     res = api.monitoringGetEnterpriseEdgeLinkStatus(body=body)
#     print(res)
# except ApiException as e:
#     print(e)


# ===================================


# BENCHMARKS
# ===================================


def sync_benchmark_call(cb, body, iterations):
    import time
    start_time = time.time()
    print(f'Starting sync benchmark of function {cb.__name__} at {time.asctime(time.localtime())}. '
          f'Will be executed {iterations} times')
    for times in range(iterations):
        cb(body=body)
    time_elapsed = time.time() - start_time
    print(f'It took {time_elapsed} seconds to perform the {cb.__name__} task {iterations} times')


def pass_callback(args):
    pass


@async_to_sync
async def async_benchmark_call(cb, body, iterations):
    import time
    promises = list()
    start_time = time.time()
    print(f'Starting sync benchmark of function {cb.__name__} at {time.asctime(time.localtime())}. '
          f'Will be executed {iterations} times')
    for times in range(iterations):
        promises.append(cb(body=body, callback=pass_callback))
    for promise in promises:
        promise.join()
    time_elapsed = time.time() - start_time
    print(f'It took {time_elapsed} seconds to perform the {cb.__name__} task {iterations} times')

# CALLS
# HINT: SYNC ONES WONT WORK
# sync_benchmark_call(api.metricsGetEdgeLinkMetrics, {"enterpriseId": 1, "id": 3987}, 9000)
# sync_benchmark_call(api.edgeGetEdge, {"enterpriseId": 1, "id": 3987}, 4800)
# async_benchmark_call(api.edgeGetEdge, {"enterpriseId": 1, "id": 3987}, 4800)
# async_benchmark_call(api.metricsGetEdgeLinkMetrics, {"enterpriseId": 1, "id": 3987}, 9000)
# ===================================
