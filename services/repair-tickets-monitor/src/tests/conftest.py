from tests.fixtures.bruin import *
from tests.fixtures.instances import *
from tests.fixtures.rta import *
from tests.fixtures.rpc import *


@pytest.fixture(scope='function')
def ticket_details_1():
    return {
        'ticketDetails': [
            {
                'detailID': 5583073, 'detailType': 'Repair_WTN', 'detailStatus': 'C', 'detailValue': 'VC05200085762',
                'assignedToName': '0', 'currentTaskID': None, 'currentTaskName': None, 'lastUpdatedBy': 385677,
                'lastUpdatedAt': '2021-01-07T17:59:12.523-05:00'
            }],  # noqa
        'ticketNotes': [{
            'noteId': 77127141, 'noteValue': '1/7/2021 3:34:01 PM\n', 'serviceNumber': ['VC05200085666'],
            'createdDate': '2021-01-07T15:34:04.057-05:00', 'creator': 'api_1@bruin.com'
        },
            {
                'noteId': 771271561,
                'noteValue': "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                             'Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for '
                             'Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 '
                             'Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) '
                             '\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044'
                             '/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe'
                             '/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge'
                             '/2044/links/]  \n \n',
                'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:34:26.48-05:00',
                'creator': 'api_1@bruin.com'
            },
            {
                'noteId': 771271562,
                'noteValue': "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                             'Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for '
                             'Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 '
                             'Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) '
                             '\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044'
                             '/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe'
                             '/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge'
                             '/2044/links/]  \n \n',
                'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:34:26.48-05:00',
                'creator': 'api_1@bruin.com'
            },
            {
                'noteId': 771271563,
                'noteValue': "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                             'Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for '
                             'Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 '
                             'Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) '
                             '\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044'
                             '/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe'
                             '/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge'
                             '/2044/links/]  \n \n',
                'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:34:26.48-05:00',
                'creator': 'api_1@bruin.com'
            }, {
                'noteId': 771271574,
                'noteValue': "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                             'Utilization \nInterface: GE2 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for '
                             'Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 '
                             'Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) '
                             '\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044'
                             '/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe'
                             '/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge'
                             '/2044/links/]  \n \n',
                'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:34:26.48-05:00',
                'creator': 'api_1@bruin.com'
            }, {
                'noteId': 77127877,
                'noteValue': 'Links\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | '
                             'Bandwidth\tPre-Notifications\tAlerts\tSignal\tLatency\tJitter\tPacket Loss\t\nComcast '
                             'Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t231.36 kbps27.15 Mbps\n20.47 '
                             'Mbps189.21 Mbps\tEdit\tEdit\tn/a\t18 msec\n9 msec\t0 msec\n0 msec\t0.00%\n0.00%\t\nApex '
                             '10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t5.83 Mbps9.94 '
                             'Mbps\n9.32 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t9 msec\n11 msec\t0 msec\n0 '
                             'msec\t0.00%\n0.00%\t',
                'serviceNumber': ['VC05200085762'],
                'createdDate': '2021-01-07T15:49:19.41-05:00',
                'creator': 'hchauhan@mettel.net'
            },
            {
                'noteId': 77128120, 'noteValue': 'Unresolve Action: Holmdel NOC Investigate ',
                'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:54:43.647-05:00',
                'creator': 'api_1@bruin.com'
            }, {
                'noteId': 77128126,
                'noteValue': "#*MetTel's IPA*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: "
                             'Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) '
                             '\nInterval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \nThroughput ('
                             'Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% ('
                             '8903.7 Kbps) \nLinks:  ['
                             'Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  ['
                             'QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  ['
                             'Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links'
                             '/]  \n \n\nTimeStamp: 2021-01-07 15:54:44.279607-05:00',
                'serviceNumber': ['VC05200085762'],
                'createdDate': '2021-01-07T15:54:47.443-05:00',
                'creator': 'api_1@bruin.com'
            },
            {
                'noteId': 77128127,
                'noteValue': '#*Automation Engine*#\nEdge Name: CA-HEALDSBURG-3871B-TS-DI\nTrouble: Jitter\nInterface: '
                             'GE2\nName: 170.39.161.40\nThreshold: 30\nInterval for Scan: 20\n'
                             'Scan Time: 2021-02-17 00:45:41.092507-05:00\nTransfer: 54.5\n'
                             'Links: Edge  - QoE  - Transport ',
                'serviceNumber': ['VC05200085762'],
                'createdDate': '2021-01-07T15:54:47.443-05:00',
                'creator': 'api_1@bruin.com'
            }
        ]  # noqa
    }


@pytest.fixture(scope='function')
def ticket_details_no_service():
    return {
        'ticketDetails': [
            {
                'detailID': 5583073, 'detailType': 'Repair_WTN', 'detailStatus': 'C', 'detailValue': 'VC05200085762',
                'assignedToName': '0', 'currentTaskID': None, 'currentTaskName': None, 'lastUpdatedBy': 385677,
                'lastUpdatedAt': '2021-01-07T17:59:12.523-05:00'
            }],  # noqa
        'ticketNotes': [
            {
                'noteId': 771271561,
                'noteValue': "#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over "
                             'Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for '
                             'Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 '
                             'Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) '
                             '\nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044'
                             '/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe'
                             '/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge'
                             '/2044/links/]  \n \n',
                'createdDate': '2021-01-07T15:34:26.48-05:00',
                'creator': 'api_1@bruin.com'
            }
        ]  # noqa
    }
