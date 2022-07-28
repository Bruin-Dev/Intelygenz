from collections import defaultdict

import pytest
from application.actions.bandwidth_reports import BandwidthReports
from application.actions.service_affecting_monitor_reports import ServiceAffectingMonitorReports
from config import testconfig
from tests.fixtures.bruin import *
from tests.fixtures.custom_objects import *
from tests.fixtures.customer_cache import *
from tests.fixtures.instances import *
from tests.fixtures.misc import *
from tests.fixtures.rpc import *
from tests.fixtures.velocloud import *

# Scopes
# - function
# - module
# - session


@pytest.fixture(scope="function")
def service_affecting_monitor_reports(
    event_bus,
    logger,
    scheduler,
    template_repository,
    bruin_repository,
    notifications_repository,
    email_repository,
    customer_cache_repository,
):
    return ServiceAffectingMonitorReports(
        event_bus,
        logger,
        scheduler,
        testconfig,
        template_repository,
        bruin_repository,
        notifications_repository,
        email_repository,
        customer_cache_repository,
    )


@pytest.fixture(scope="function")
def bandwidth_reports(
    logger,
    scheduler,
    velocloud_repository,
    bruin_repository,
    trouble_repository,
    customer_cache_repository,
    email_repository,
    utils_repository,
    template_repository,
):
    return BandwidthReports(
        logger,
        scheduler,
        testconfig,
        velocloud_repository,
        bruin_repository,
        trouble_repository,
        customer_cache_repository,
        email_repository,
        utils_repository,
        template_repository,
    )


@pytest.fixture(scope="function")
def report():
    return {
        "name": "Report - Bandwidth Utilization",
        "type": "bandwidth_utilization",
        "value": "Bandwidth Over Utilization",
        "crontab": "0 8 * * *",
        "threshold": 3,
        "client_id": 83109,
        "trailing_days": 14,
        "recipient": "mettel@intelygenz.com",
    }


@pytest.fixture(scope="function")
def report_jitter():
    return {
        "name": "Jitter",
        "type": "jitter",
        "value": "Jitter",
        "crontab": "20 16 * * *",
        "threshold": 1,
        "trailing_days": 14,
        "recipient": "mettel@intelygenz.com",
    }


@pytest.fixture(scope="function")
def ticket_1():
    return {
        "clientID": 83109,
        "clientName": "RSI",
        "ticketID": 5081250,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
        "ticketStatus": "Closed",
        "address": {
            "address": "621 Hill Ave",
            "city": "Nashville",
            "state": "TN",
            "zip": "37210-4714",
            "country": "USA",
        },
        "createDate": "1/7/2021 8:34:22 PM",
        "createdBy": "Intelygenz Ai",
        "creationNote": None,
        "resolveDate": "1/7/2021 10:58:55 PM",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/7/2021 8:54:47 PM Intelygenz Ai",
        "nextScheduledDate": "1/14/2021 5:00:00 AM",
        "flags": "",
        "severity": "3",
    }  # noqa


@pytest.fixture(scope="function")
def ticket_details_1():
    return {
        "ticketDetails": [
            {
                "detailID": 5583073,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-07T17:59:12.523-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77127141,
                "noteValue": "1/7/2021 3:34:01 PM\n",
                "serviceNumber": ["VC05200085666"],
                "createdDate": "2021-01-07T15:34:04.057-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771271561,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771271562,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771271563,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771271574,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE2 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77127877,
                "noteValue": "Links\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\tLatency\tJitter\tPacket Loss\t\nComcast "
                "Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t231.36 kbps27.15 Mbps\n20.47 "
                "Mbps189.21 Mbps\tEdit\tEdit\tn/a\t18 msec\n9 msec\t0 msec\n0 msec\t0.00%\n0.00%\t\nApex "
                "10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t5.83 Mbps9.94 "
                "Mbps\n9.32 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t9 msec\n11 msec\t0 msec\n0 "
                "msec\t0.00%\n0.00%\t",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:49:19.41-05:00",
                "creator": "hchauhan@mettel.net",
            },
            {
                "noteId": 77128120,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:43.647-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77128126,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \nThroughput ("
                "Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% ("
                "8903.7 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-07 15:54:44.279607-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77128127,
                "noteValue": "#*Automation Engine*#\nEdge Name: CA-HEALDSBURG-3871B-TS-DI\nTrouble: Jitter\nInterface: "
                "GE2\nName: 170.39.161.40\nThreshold: 30\nInterval for Scan: 20\n"
                "Scan Time: 2021-02-17 00:45:41.092507-05:00\nTransfer: 54.5\n"
                "Links: Edge  - QoE  - Transport ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def ticket_1_1():
    return {
        "clientID": 83109,
        "clientName": "RSI",
        "ticketID": 50812501,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
        "ticketStatus": "Closed",
        "address": {
            "address": "621 Hill Ave",
            "city": "Nashville",
            "state": "TN",
            "zip": "37210-4714",
            "country": "USA",
        },
        "createDate": "1/7/2021 8:34:22 PM",
        "createdBy": "Intelygenz Ai",
        "creationNote": None,
        "resolveDate": "1/7/2021 10:58:55 PM",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/7/2021 8:54:47 PM Intelygenz Ai",
        "nextScheduledDate": "1/14/2021 5:00:00 AM",
        "flags": "",
        "severity": "3",
    }  # noqa


@pytest.fixture(scope="function")
def ticket_details_1_1():
    return {
        "ticketDetails": [
            {
                "detailID": 5583073,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-07T17:59:12.523-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77127141,
                "noteValue": "1/7/2021 3:34:01 PM\n",
                "serviceNumber": ["VC05200085666"],
                "createdDate": "2021-01-07T15:34:04.057-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715611,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715621,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715631,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715741,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE2 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771278771,
                "noteValue": "Links\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\tLatency\tJitter\tPacket Loss\t\nComcast "
                "Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t231.36 kbps27.15 Mbps\n20.47 "
                "Mbps189.21 Mbps\tEdit\tEdit\tn/a\t18 msec\n9 msec\t0 msec\n0 msec\t0.00%\n0.00%\t\nApex "
                "10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t5.83 Mbps9.94 "
                "Mbps\n9.32 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t9 msec\n11 msec\t0 msec\n0 "
                "msec\t0.00%\n0.00%\t",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:49:19.41-05:00",
                "creator": "hchauhan@mettel.net",
            },
            {
                "noteId": 771281201,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:43.647-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771281261,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \nThroughput ("
                "Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% ("
                "8903.7 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-07 15:54:44.279607-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771281271,
                "noteValue": "#*Automation Engine*#\nEdge Name: CA-HEALDSBURG-3871B-TS-DI\nTrouble: Jitter\nInterface: "
                "GE2\nName: 170.39.161.40\nThreshold: 30\nInterval for Scan: 20\n"
                "Scan Time: 2021-02-17 00:45:41.092507-05:00\nTransfer: 54.5\n"
                "Links: Edge  - QoE  - Transport ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def ticket_1_2():
    return {
        "clientID": 83109,
        "clientName": "RSI",
        "ticketID": 50812502,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
        "ticketStatus": "Closed",
        "address": {
            "address": "621 Hill Ave",
            "city": "Nashville",
            "state": "TN",
            "zip": "37210-4714",
            "country": "USA",
        },
        "createDate": "1/7/2021 8:34:22 PM",
        "createdBy": "Intelygenz Ai",
        "creationNote": None,
        "resolveDate": "1/7/2021 10:58:55 PM",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/7/2021 8:54:47 PM Intelygenz Ai",
        "nextScheduledDate": "1/14/2021 5:00:00 AM",
        "flags": "",
        "severity": "3",
    }  # noqa


@pytest.fixture(scope="function")
def ticket_details_1_2():
    return {
        "ticketDetails": [
            {
                "detailID": 5583073,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-07T17:59:12.523-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77127141,
                "noteValue": "1/7/2021 3:34:01 PM\n",
                "serviceNumber": ["VC05200085666"],
                "createdDate": "2021-01-07T15:34:04.057-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715612,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715622,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715632,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 7712715742,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE2 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771278772,
                "noteValue": "Links\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\tLatency\tJitter\tPacket Loss\t\nComcast "
                "Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t231.36 kbps27.15 Mbps\n20.47 "
                "Mbps189.21 Mbps\tEdit\tEdit\tn/a\t18 msec\n9 msec\t0 msec\n0 msec\t0.00%\n0.00%\t\nApex "
                "10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t5.83 Mbps9.94 "
                "Mbps\n9.32 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t9 msec\n11 msec\t0 msec\n0 "
                "msec\t0.00%\n0.00%\t",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:49:19.41-05:00",
                "creator": "hchauhan@mettel.net",
            },
            {
                "noteId": 771281202,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:43.647-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771281262,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \nThroughput ("
                "Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% ("
                "8903.7 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-07 15:54:44.279607-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 771281272,
                "noteValue": "#*Automation Engine*#\nEdge Name: CA-HEALDSBURG-3871B-TS-DI\nTrouble: Jitter\nInterface: "
                "GE2\nName: 170.39.161.40\nThreshold: 30\nInterval for Scan: 20\n"
                "Scan Time: 2021-02-17 00:45:41.092507-05:00\nTransfer: 54.5\n"
                "Links: Edge  - QoE  - Transport ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def filter_ticket_details_1():
    return {
        "ticketDetails": [
            {
                "detailID": 5583073,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-07T17:59:12.523-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77127156,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization "
                "\nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan "
                "Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 Kbps \nBandwidth ("
                "Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  "
                "\n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:34:26.48-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77128126,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \nThroughput ("
                "Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% ("
                "8903.7 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-07 15:54:44.279607-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77128127,
                "noteValue": "#*Automation Engine*#\nEdge Name: CA-HEALDSBURG-3871B-TS-DI\nTrouble: Jitter\nInterface: "
                "GE2\nName: 170.39.161.40\nThreshold: 30\nInterval for Scan: 20\n"
                "Scan Time: 2021-02-17 00:45:41.092507-05:00\nTransfer: 54.5\n"
                "Links: Edge  - QoE  - Transport ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def ticket_2():
    return {
        "clientID": 83109,
        "clientName": "RSI",
        "ticketID": 5075176,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
        "ticketStatus": "Closed",
        "address": {
            "address": "621 Hill Ave",
            "city": "Nashville",
            "state": "TN",
            "zip": "37210-4714",
            "country": "USA",
        },
        "createDate": "1/5/2021 9:22:11 PM",
        "createdBy": "Intelygenz Ai",
        "creationNote": None,
        "resolveDate": "1/6/2021 10:34:51 PM",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/6/2021 1:58:04 PM Intelygenz Ai",
        "nextScheduledDate": "1/12/2021 5:00:00 AM",
        "flags": "",
        "severity": "3",
    }  # noqa


@pytest.fixture(scope="function")
def ticket_details_2():
    return {
        "ticketDetails": [
            {
                "detailID": 5576149,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085763",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-06T17:35:10.317-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77051076,
                "noteValue": "1/5/2021 4:22:09 PM\n",
                "serviceNumber": ["VC05200085763"],
                "createdDate": "2021-01-05T16:22:11.247-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77051080,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 16:22:09.661410-05:00 \nThroughput (Receive): 8150.85 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085763"],
                "createdDate": "2021-01-05T16:22:24.03-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77076710,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085763"],
                "createdDate": "2021-01-06T08:57:35.85-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77076719,
                "noteValue": "#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \nThroughput ("
                "Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00",
                "serviceNumber": ["VC05200085763"],
                "createdDate": "2021-01-06T08:58:04.083-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77076720,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \nThroughput ("
                "Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00",
                "serviceNumber": ["VC05200085763"],
                "createdDate": "2021-01-06T08:58:04.177-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77128129,
                "noteValue": "#*Automation Engine*#\nEdge Name: CA-HEALDSBURG-3871B-TS-DI\nTrouble: Jitter\nInterface: "
                "GE2\nName: 170.39.161.40\nThreshold: 30\nInterval for Scan: 20\n"
                "Scan Time: 2021-02-17 00:45:41.092507-05:00\nTransfer: 54.5\n"
                "Links: Edge  - QoE  - Transport ",
                "serviceNumber": ["VC05200085763"],
                "createdDate": "2021-01-07T15:54:47.443-05:00",
                "creator": "api_1@bruin.com",
            },
        ]
        # noqa
    }


@pytest.fixture(scope="function")
def filter_ticket_details_2():
    return {
        "ticketDetails": [
            {
                "detailID": 5576149,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-06T17:35:10.317-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77051080,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 16:22:09.661410-05:00 \nThroughput (Receive): 8150.85 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T16:22:24.03-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77076719,
                "noteValue": "#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \nThroughput ("
                "Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-06T08:58:04.083-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77076720,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \nThroughput ("
                "Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-06T08:58:04.177-05:00",
                "creator": "api_1@bruin.com",
            },
        ]
        # noqa
    }


@pytest.fixture(scope="function")
def ticket_3():
    return {
        "clientID": 83109,
        "clientName": "RSI",
        "ticketID": 5074441,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
        "ticketStatus": "Closed",
        "address": {
            "address": "621 Hill Ave",
            "city": "Nashville",
            "state": "TN",
            "zip": "37210-4714",
            "country": "USA",
        },
        "createDate": "1/5/2021 6:49:25 PM",
        "createdBy": "Intelygenz Ai",
        "creationNote": None,
        "resolveDate": "1/5/2021 7:34:09 PM",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/5/2021 7:33:34 PM Dhruv Patel",
        "nextScheduledDate": "1/12/2021 5:00:00 AM",
        "flags": "",
        "severity": "3",
    }  # noqa


@pytest.fixture(scope="function")
def ticket_details_3():
    return {
        "ticketDetails": [
            {
                "detailID": 5575534,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085764",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T14:34:23.72-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77043435,
                "noteValue": "1/5/2021 1:49:21 PM\n",
                "serviceNumber": ["VC05200085764"],
                "createdDate": "2021-01-05T13:49:25.337-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77043439,
                "noteValue": "#*MetTel's IPA*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 13:49:21.416728-05:00 \nThroughput (Receive): 8271.982 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085764"],
                "createdDate": "2021-01-05T13:49:27.65-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77045257,
                "noteValue": "BW utilization is normal compared to BYOB ckt.\nLink is stable.\n\nLinks\tCloud "
                "Status\tVPN Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\t\nComcast Cable (BYOB) "
                "\n173.10.211.109\t\t\tGE2 (Ethernet)\t1.95 Mbps27.15 Mbps\n6.11 Mbps189.21 "
                "Mbps\tEdit\tEdit\tn/a\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 ("
                "Ethernet)\t3.02 Mbps9.94 Mbps\n1.45 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t\n \n",
                "serviceNumber": ["VC05200085764"],
                "createdDate": "2021-01-05T14:33:34.623-05:00",
                "creator": "dpatel@mettel.net",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def filter_ticket_details_3():
    return {
        "ticketDetails": [
            {
                "detailID": 5575534,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T14:34:23.72-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77043439,
                "noteValue": "#*MetTel's IPA*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 13:49:21.416728-05:00 \nThroughput (Receive): 8271.982 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T13:49:27.65-05:00",
                "creator": "api_1@bruin.com",
            }
        ],
    }


@pytest.fixture(scope="function")
def ticket_4():
    return {
        "clientID": 83109,
        "clientName": "RSI",
        "ticketID": 5073652,
        "category": "SD-WAN",
        "topic": "Service Affecting Trouble",
        "referenceTicketNumber": 0,
        "ticketStatus": "Closed",
        "address": {
            "address": "621 Hill Ave",
            "city": "Nashville",
            "state": "TN",
            "zip": "37210-4714",
            "country": "USA",
        },
        "createDate": "1/5/2021 3:29:39 PM",
        "createdBy": "Intelygenz Ai",
        "creationNote": None,
        "resolveDate": "1/5/2021 5:06:54 PM",
        "resolvedby": None,
        "closeDate": None,
        "closedBy": None,
        "lastUpdate": None,
        "updatedBy": None,
        "mostRecentNote": "1/5/2021 4:52:05 PM Intelygenz Ai",
        "nextScheduledDate": "1/12/2021 5:00:00 AM",
        "flags": "",
        "severity": "3",
    }  # noqa


@pytest.fixture(scope="function")
def ticket_details_4():
    return {
        "ticketDetails": [
            {
                "detailID": 5574754,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085765",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T12:07:31.707-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77034430,
                "noteValue": "1/5/2021 10:29:37 AM\n",
                "serviceNumber": ["VC05200085765"],
                "createdDate": "2021-01-05T10:29:38.857-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77034460,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 10:29:22.043598-05:00 \nThroughput (Receive): 8365.164 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085765"],
                "createdDate": "2021-01-05T10:30:21.64-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77034984,
                "noteValue": "Bandwidth utilization is nothing compared to BYOB ckt.\n\nLinks\tCloud Status\tVPN "
                "Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\t\nComcast Cable (BYOB) "
                "\n173.10.211.109\t\t\tGE2 (Ethernet)\t1.81 Mbps27.15 Mbps\n6.91 Mbps189.21 "
                "Mbps\tEdit\tEdit\tn/a\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 ("
                "Ethernet)\t428.21 kbps9.94 Mbps\n6.59 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t\n \nLink is "
                "stable.",
                "serviceNumber": ["VC05200085765"],
                "createdDate": "2021-01-05T10:39:43.817-05:00",
                "creator": "dpatel@mettel.net",
            },
            {
                "noteId": 77039079,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085765"],
                "createdDate": "2021-01-05T11:52:05.01-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77039080,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-05 11:51:39.347045-05:00 \nThroughput ("
                "Receive): 8139.369 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-05 11:52:05.664662-05:00",
                "serviceNumber": ["VC05200085765"],
                "createdDate": "2021-01-05T11:52:05.603-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def filter_ticket_details_4():
    return {
        "ticketDetails": [
            {
                "detailID": 5574754,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T12:07:31.707-05:00",
            }
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77034460,
                "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization "
                "\nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan "
                "Time: 2021-01-05 10:29:22.043598-05:00 \nThroughput (Receive): 8365.164 Kbps \nBandwidth ("
                "Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  "
                "\n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:30:21.64-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77039080,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-05 11:51:39.347045-05:00 \nThroughput ("
                "Receive): 8139.369 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-05 11:52:05.664662-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T11:52:05.603-05:00",
                "creator": "api_1@bruin.com",
            },
        ],
    }


@pytest.fixture(scope="function")
def ticket_extra_details_details():
    return {
        "ticketDetails": [
            {
                "detailID": 5574754,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T12:07:31.707-05:00",
            },
            {
                "detailID": 5574689,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200089956",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T12:07:31.707-05:00",
            },
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77034430,
                "noteValue": "1/5/2021 10:29:37 AM\n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:29:38.857-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77034460,
                "noteValue": "#*MetTel's IPA*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 10:29:22.043598-05:00 \nThroughput (Receive): 8365.164 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:30:21.64-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77034984,
                "noteValue": "Bandwidth utilization is nothing compared to BYOB ckt.\n\nLinks\tCloud Status\tVPN "
                "Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\t\nComcast Cable (BYOB) "
                "\n173.10.211.109\t\t\tGE2 (Ethernet)\t1.81 Mbps27.15 Mbps\n6.91 Mbps189.21 "
                "Mbps\tEdit\tEdit\tn/a\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 ("
                "Ethernet)\t428.21 kbps9.94 Mbps\n6.59 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t\n \nLink is "
                "stable.",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:39:43.817-05:00",
                "creator": "dpatel@mettel.net",
            },
            {
                "noteId": 77039079,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T11:52:05.01-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77039080,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-05 11:51:39.347045-05:00 \nThroughput ("
                "Receive): 8139.369 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-05 11:52:05.664662-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T11:52:05.603-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def ticket_no_details():
    return {
        "ticketDetails": [
            {
                "detailID": 5574754,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200089874",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T12:07:31.707-05:00",
            },
        ],  # noqa
        "ticketNotes": [
            {
                "noteId": 77034430,
                "noteValue": "1/5/2021 10:29:37 AM\n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:29:38.857-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77034460,
                "noteValue": "#*MetTel's IPA*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                "Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for "
                "Scan: 20 \nScan Time: 2021-01-05 10:29:22.043598-05:00 \nThroughput (Receive): 8365.164 "
                "Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) "
                "\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044"
                "/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe"
                "/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                "/2044/links/]  \n \n",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:30:21.64-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77034984,
                "noteValue": "Bandwidth utilization is nothing compared to BYOB ckt.\n\nLinks\tCloud Status\tVPN "
                "Status\tInterface (WAN Type)\tThroughput | "
                "Bandwidth\tPre-Notifications\tAlerts\tSignal\t\nComcast Cable (BYOB) "
                "\n173.10.211.109\t\t\tGE2 (Ethernet)\t1.81 Mbps27.15 Mbps\n6.91 Mbps189.21 "
                "Mbps\tEdit\tEdit\tn/a\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 ("
                "Ethernet)\t428.21 kbps9.94 Mbps\n6.59 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t\n \nLink is "
                "stable.",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T10:39:43.817-05:00",
                "creator": "dpatel@mettel.net",
            },
            {
                "noteId": 77039079,
                "noteValue": "Unresolve Action: Holmdel NOC Investigate ",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T11:52:05.01-05:00",
                "creator": "api_1@bruin.com",
            },
            {
                "noteId": 77039080,
                "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) "
                "\nInterval for Scan: 20 \nScan Time: 2021-01-05 11:51:39.347045-05:00 \nThroughput ("
                "Receive): 8139.369 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% ("
                "7914.4 Kbps) \nLinks:  ["
                "Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ["
                "QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ["
                "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links"
                "/]  \n \n\nTimeStamp: 2021-01-05 11:52:05.664662-05:00",
                "serviceNumber": ["VC05200085762"],
                "createdDate": "2021-01-05T11:52:05.603-05:00",
                "creator": "api_1@bruin.com",
            },
        ],  # noqa
    }


@pytest.fixture(scope="function")
def customer_cache():
    return [
        {
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 519},
            "last_contact": "2021-01-29T11:36:30.000Z",
            "logical_ids": [
                {"interface_name": "GE1", "logical_id": "42:a6:77:be:2f:cc:0000"},
                {"interface_name": "GE2", "logical_id": "f6:4b:2a:72:0f:72:0000"},
            ],
            "serial_number": "VC05200085761",
            "bruin_client_info": {"client_id": 87055, "client_name": "Benchmark Senior Living - Network"},
        },
        {
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 951},
            "last_contact": "2021-01-29T11:36:10.000Z",
            "logical_ids": [
                {"interface_name": "GE1", "logical_id": "82:b2:34:20:60:fa:0000"},
                {"interface_name": "GE2", "logical_id": "00:04:2d:0b:65:34:0000"},
            ],
            "serial_number": "VC05200025943",
            "bruin_client_info": {"client_id": 87055, "client_name": "Benchmark Senior Living - Network"},
        },
        {
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 1561},
            "last_contact": "2020-10-15T21:06:31.000Z",
            "logical_ids": [
                {"interface_name": "GE1", "logical_id": "6a:ee:96:dc:43:10:0000"},
                {"interface_name": "GE2", "logical_id": "00:90:1a:a0:01:04:0000"},
            ],
            "serial_number": "VC05200085762",
            "bruin_client_info": {"client_id": 85134, "client_name": "Benchmark Senior Living - Wireless"},
        },
        {
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 1561},
            "last_contact": "2020-10-15T21:06:31.000Z",
            "logical_ids": [
                {"interface_name": "GE1", "logical_id": "6a:ee:96:dc:43:10:0000"},
                {"interface_name": "GE2", "logical_id": "00:90:1a:a0:01:04:0000"},
            ],
            "serial_number": "VC05200085761",
            "bruin_client_info": {"client_id": 85134, "client_name": "Benchmark Senior Living - Wireless"},
        },
        {
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 1561},
            "last_contact": "2020-10-15T21:06:31.000Z",
            "logical_ids": [
                {"interface_name": "GE1", "logical_id": "6a:ee:96:dc:43:10:0000"},
                {"interface_name": "GE2", "logical_id": "00:90:1a:a0:01:04:0000"},
            ],
            "serial_number": "VC05200085763",
            "bruin_client_info": {"client_id": 85134, "client_name": "Benchmark Senior Living - Wireless"},
        },
        {
            "edge": {"host": "mettel.velocloud.net", "enterprise_id": 100, "edge_id": 1561},
            "last_contact": "2020-10-15T21:06:31.000Z",
            "logical_ids": [
                {"interface_name": "GE1", "logical_id": "6a:ee:96:dc:43:10:0000"},
                {"interface_name": "GE2", "logical_id": "00:90:1a:a0:01:04:0000"},
            ],
            "serial_number": "VC05200085764",
            "bruin_client_info": {"client_id": 85134, "client_name": "Benchmark Senior Living - Wireless"},
        },
    ]


@pytest.fixture(scope="function")
def list_customer_cache_serials():
    return ["VC05200085762", "VC05200025943", "VC05400003861", "VC05400003862", "VC05400003863", "VC05400003864"]


@pytest.fixture(scope="function")
def response_customer_cache(customer_cache):
    return {"body": customer_cache, "status": 200}


@pytest.fixture(scope="function")
def response_empty_customer_cache():
    return {"body": [], "status": 200}


@pytest.fixture(scope="function")
def response_bad_status_customer_cache():
    return {"body": [], "status": 404}


@pytest.fixture(scope="function")
def response_bruin_with_all_tickets_without_details(ticket_1, ticket_2, ticket_3, ticket_4):
    return {"body": [ticket_1, ticket_2, ticket_3, ticket_4], "status": 200}


@pytest.fixture(scope="function")
def response_bruin_with_no_tickets():
    return {"body": [], "status": 200}


@pytest.fixture(scope="function")
def response_bruin_401():
    return {"body": "error 401", "status": 401}


@pytest.fixture(scope="function")
def response_bruin_403():
    return {"body": "error 403", "status": 403}


@pytest.fixture(scope="function")
def response_bruin_with_error():
    return {"body": "Some error", "status": 400}


@pytest.fixture(scope="function")
def response_bruin_with_all_tickets(
    ticket_1, ticket_details_1, ticket_2, ticket_details_2, ticket_3, ticket_details_3, ticket_4, ticket_details_4
):
    return {
        ticket_1["ticketID"]: {"ticket": ticket_1, "ticket_details": ticket_details_1},
        ticket_2["ticketID"]: {"ticket": ticket_2, "ticket_details": ticket_details_2},
        ticket_3["ticketID"]: {"ticket": ticket_3, "ticket_details": ticket_details_3},
        ticket_4["ticketID"]: {"ticket": ticket_4, "ticket_details": ticket_details_4},
    }


@pytest.fixture(scope="function")
def response_bruin_with_all_tickets_complete(
    ticket_1,
    ticket_details_1,
    ticket_1_1,
    ticket_details_1_1,
    ticket_1_2,
    ticket_details_1_2,
    ticket_2,
    ticket_details_2,
    ticket_3,
    ticket_details_3,
    ticket_4,
    ticket_details_4,
):
    return {
        ticket_1["ticketID"]: {"ticket": ticket_1, "ticket_details": ticket_details_1},
        ticket_1_1["ticketID"]: {"ticket": ticket_1_1, "ticket_details": ticket_details_1_1},
        ticket_1_2["ticketID"]: {"ticket": ticket_1_2, "ticket_details": ticket_details_1_2},
        ticket_2["ticketID"]: {"ticket": ticket_2, "ticket_details": ticket_details_2},
        ticket_3["ticketID"]: {"ticket": ticket_3, "ticket_details": ticket_details_3},
        ticket_4["ticketID"]: {"ticket": ticket_4, "ticket_details": ticket_details_4},
    }


@pytest.fixture(scope="function")
def response_bruin_one_tickets(ticket_1, ticket_extra_details_details):
    return {
        ticket_1["ticketID"]: {"ticket": ticket_1, "ticket_details": ticket_extra_details_details},
    }


@pytest.fixture(scope="function")
def response_bruin_one_tickets_no_details(ticket_1, ticket_no_details):
    return {
        ticket_1["ticketID"]: {"ticket": ticket_1, "ticket_details": ticket_no_details},
    }


@pytest.fixture(scope="function")
def filter_response_bruin_with_all_tickets(
    ticket_1,
    filter_ticket_details_1,
    ticket_2,
    filter_ticket_details_2,
    ticket_3,
    filter_ticket_details_3,
    ticket_4,
    filter_ticket_details_4,
):
    return {
        ticket_1["ticketID"]: {"ticket": ticket_1, "ticket_details": filter_ticket_details_1},
        ticket_2["ticketID"]: {"ticket": ticket_2, "ticket_details": filter_ticket_details_2},
        ticket_3["ticketID"]: {"ticket": ticket_3, "ticket_details": filter_ticket_details_3},
        ticket_4["ticketID"]: {"ticket": ticket_4, "ticket_details": filter_ticket_details_4},
    }


@pytest.fixture(scope="function")
def response_bruin_with_all_tickets_with_exception():
    return None


@pytest.fixture(scope="function")
def response_mapped_tickets(
    ticket_1, ticket_details_1, ticket_2, ticket_details_2, ticket_3, ticket_details_3, ticket_4, ticket_details_4
):
    ret = defaultdict(list)
    ret[ticket_details_1["ticketDetails"][0]["detailValue"]].append(
        {"ticket": ticket_1, "ticket_details": ticket_details_1}
    )
    ret[ticket_details_2["ticketDetails"][0]["detailValue"]].append(
        {"ticket": ticket_2, "ticket_details": ticket_details_2}
    )
    ret[ticket_details_3["ticketDetails"][0]["detailValue"]].append(
        {"ticket": ticket_3, "ticket_details": ticket_details_3}
    )
    ret[ticket_details_4["ticketDetails"][0]["detailValue"]].append(
        {"ticket": ticket_4, "ticket_details": ticket_details_4}
    )
    return ret


@pytest.fixture(scope="function")
def response_mapped_one_tickets(ticket_1, ticket_extra_details_details):
    ret = defaultdict(list)
    ret[ticket_extra_details_details["ticketDetails"][0]["detailValue"]].append(
        {"ticket": ticket_1, "ticket_details": ticket_extra_details_details}
    )
    return ret


@pytest.fixture(scope="function")
def response_prepare_items_for_report(ticket_1, ticket_2, ticket_3, ticket_4, ticket_details_1):
    return [
        {
            "customer": {"client_id": ticket_1["clientID"], "client_name": "RSI"},
            "location": ticket_1["address"],
            "serial_number": ticket_details_1["ticketDetails"][0]["detailValue"],
            "number_of_tickets": 4,
            "bruin_tickets_id": [
                ticket_1["ticketID"],
                ticket_2["ticketID"],
                ticket_3["ticketID"],
                ticket_4["ticketID"],
            ],
            "interfaces": ["GE1"],
        }
    ]


@pytest.fixture(scope="function")
def filtered_affecting_tickets(ticket_1, ticket_2, ticket_3, ticket_4):
    return [
        {
            "ticket_id": 5081250,
            "ticket": ticket_1,
            "ticket_detail": {
                "detailID": 5583073,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-07T17:59:12.523-05:00",
            },
            "ticket_notes": [
                {
                    "noteId": 77127156,
                    "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                    "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M "
                    "(MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: "
                    "2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 Kbps \n"
                    "Bandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps)"
                    " \nLinks:  "
                    "[Edge|https://metvco03.mettel.net/#!/operator"
                    "/customer/124/monitor/edge/2044/]  -  "
                    "[QoE|https://metvco03.mettel.net/#!/"
                    "operator/customer/124/monitor/edge/2044/qoe/]  -  "
                    "[Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/links/]  \n \n",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-07T15:34:26.48-05:00",
                    "creator": "api_1@bruin.com",
                },
                {
                    "noteId": 77128126,
                    "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge "
                    "Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \n"
                    "Interface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \n"
                    "Interval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \n"
                    "Throughput (Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \n"
                    "Threshold (Receive): 90% (8903.7 Kbps) \nLinks:  "
                    "[Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/]  -  "
                    "[QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/qoe/]  -  "
                    "[Transport|https://metvco03.mettel.net/#!/operator/customer/124"
                    "/monitor/edge/2044/links/]  \n \n\n"
                    "TimeStamp: 2021-01-07 15:54:44.279607-05:00",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-07T15:54:47.443-05:00",
                    "creator": "api_1@bruin.com",
                },
            ],
        },
        {
            "ticket_id": 5075176,
            "ticket": ticket_2,
            "ticket_detail": {
                "detailID": 5576149,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385677,
                "lastUpdatedAt": "2021-01-06T17:35:10.317-05:00",
            },
            "ticket_notes": [
                {
                    "noteId": 77051080,
                    "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                    "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M "
                    "(MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: "
                    "2021-01-05 16:22:09.661410-05:00 \nThroughput (Receive): 8150.85 Kbps \n"
                    "Bandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps)"
                    " \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/"
                    "monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/"
                    "customer/124/monitor/edge/2044/qoe/]  -  "
                    "[Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/links/]  \n \n",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-05T16:22:24.03-05:00",
                    "creator": "api_1@bruin.com",
                },
                {
                    "noteId": 77076719,
                    "noteValue": "#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: "
                    "TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: "
                    "GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \n"
                    "Interval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \n"
                    "Throughput (Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps "
                    "\nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  "
                    "[Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/"
                    "edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer"
                    "/124/monitor/edge/2044/qoe/]  -  "
                    "[Transport|https://metvco03.mettel.net/#!/operator/customer/124"
                    "/monitor/edge/2044/links/]  \n \n\n"
                    "TimeStamp: 2021-01-06 08:57:36.651254-05:00",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-06T08:58:04.083-05:00",
                    "creator": "api_1@bruin.com",
                },
                {
                    "noteId": 77076720,
                    "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: "
                    "TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \n"
                    "Interface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \n"
                    "Interval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \n"
                    "Throughput (Receive): 9196.147 Kbps \n"
                    "Bandwidth (Receive): 9893.0 Kbps \n"
                    "Threshold (Receive): 80% (7914.4 Kbps) \nLinks:  "
                    "[Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/]  -  "
                    "[QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/qoe/]  -  ["
                    "Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/links/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-06T08:58:04.177-05:00",
                    "creator": "api_1@bruin.com",
                },
            ],
        },
        {
            "ticket_id": 5074441,
            "ticket": ticket_3,
            "ticket_detail": {
                "detailID": 5575534,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T14:34:23.72-05:00",
            },
            "ticket_notes": [
                {
                    "noteId": 77043439,
                    "noteValue": "#*MetTel's IPA*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                    "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M "
                    "(MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: "
                    "2021-01-05 13:49:21.416728-05:00 \nThroughput (Receive): 8271.982 Kbps \n"
                    "Bandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): "
                    "80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator"
                    "/customer/124/monitor/edge/2044/]  -  "
                    "[QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge"
                    "/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator"
                    "/customer/124/monitor/edge/2044/links/]  \n \n",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-05T13:49:27.65-05:00",
                    "creator": "api_1@bruin.com",
                }
            ],
        },
        {
            "ticket_id": 5073652,
            "ticket": ticket_4,
            "ticket_detail": {
                "detailID": 5574754,
                "detailType": "Repair_WTN",
                "detailStatus": "C",
                "detailValue": "VC05200085762",
                "assignedToName": "0",
                "currentTaskID": None,
                "currentTaskName": None,
                "lastUpdatedBy": 385676,
                "lastUpdatedAt": "2021-01-05T12:07:31.707-05:00",
            },
            "ticket_notes": [
                {
                    "noteId": 77034460,
                    "noteValue": "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                    "Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel "
                    "CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-05 "
                    "10:29:22.043598-05:00 \nThroughput (Receive): 8365.164 Kbps \n"
                    "Bandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% "
                    "(7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator"
                    "/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net"
                    "/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https:"
                    "//metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]"
                    "  \n \n",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-05T10:30:21.64-05:00",
                    "creator": "api_1@bruin.com",
                },
                {
                    "noteId": 77039080,
                    "noteValue": "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: "
                    "TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: "
                    "GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 "
                    "\nScan Time: 2021-01-05 11:51:39.347045-05:00 \nThroughput (Receive): "
                    "8139.369 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): "
                    "80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator"
                    "/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net"
                    "/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  "
                    "[Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor"
                    "/edge/2044/links/]  \n \n\nTimeStamp: 2021-01-05 11:52:05.664662-05:00",
                    "serviceNumber": ["VC05200085762"],
                    "createdDate": "2021-01-05T11:52:05.603-05:00",
                    "creator": "api_1@bruin.com",
                },
            ],
        },
    ]


@pytest.fixture(scope="function")
def response_mapped_filter_tickets(filtered_affecting_tickets):
    ret = defaultdict(list)
    ret[filtered_affecting_tickets[0]["ticket_detail"]["detailValue"]].append(filtered_affecting_tickets[0])
    ret[filtered_affecting_tickets[1]["ticket_detail"]["detailValue"]].append(filtered_affecting_tickets[1])
    ret[filtered_affecting_tickets[2]["ticket_detail"]["detailValue"]].append(filtered_affecting_tickets[2])
    ret[filtered_affecting_tickets[3]["ticket_detail"]["detailValue"]].append(filtered_affecting_tickets[3])
    return ret


@pytest.fixture(scope="function")
def response_prepare_items_filtered_for_report(filtered_affecting_tickets):
    return [
        {
            "customer": {"client_id": filtered_affecting_tickets[0]["ticket"]["clientID"], "client_name": "RSI"},
            "location": filtered_affecting_tickets[0]["ticket"]["address"],
            "serial_number": filtered_affecting_tickets[0]["ticket_detail"]["detailValue"],
            "number_of_tickets": 4,
            "bruin_tickets_id": {
                filtered_affecting_tickets[0]["ticket_id"],
                filtered_affecting_tickets[1]["ticket_id"],
                filtered_affecting_tickets[2]["ticket_id"],
                filtered_affecting_tickets[3]["ticket_id"],
            },
            "interfaces": ["GE1"],
        }
    ]
