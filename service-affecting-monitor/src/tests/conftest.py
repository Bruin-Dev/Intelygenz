import copy
from unittest.mock import Mock
import pytest
from collections import defaultdict

from config import testconfig
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.bruin_repository import BruinRepository
from application.actions.service_affecting_monitor_reports import ServiceAffectingMonitorReports
from application.repositories.template_management import TemplateRenderer

# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def scheduler():
    return Mock()


@pytest.fixture(scope='function')
def event_bus():
    return Mock()


@pytest.fixture(scope='function')
def template_renderer():
    return TemplateRenderer(testconfig)


@pytest.fixture(scope='function')
def notifications_repository(event_bus):
    return NotificationsRepository(event_bus)


@pytest.fixture(scope='function')
def bruin_repository(event_bus, logger, notifications_repository):
    return BruinRepository(event_bus=event_bus, logger=logger, config=testconfig,
                           notifications_repository=notifications_repository)


@pytest.fixture(scope='function')
def service_affecting_monitor_reports(
        event_bus, logger, scheduler, template_renderer, bruin_repository, notifications_repository):
    return ServiceAffectingMonitorReports(event_bus, logger, scheduler, testconfig, template_renderer,
                                          bruin_repository, notifications_repository)


@pytest.fixture(scope='function')
def report():
    return {
        'name': 'Report - Bandwitdh Over Utilization',
        'type': 'bandwitdh_over_utilization',
        'crontab': '20 16 * * *',
        'threshold': 3,
        'client_id': 83109,
        'trailing_days': 14,
        'recipient': 'mettel@intelygenz.com'
    }


@pytest.fixture(scope='function')
def ticket_1():
    return {'clientID': 83109, 'clientName': 'RSI', 'ticketID': 5081250, 'category': 'SD-WAN', 'topic': 'Service Affecting Trouble', 'referenceTicketNumber': 0, 'ticketStatus': 'Closed', 'address': {'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714', 'country': 'USA'}, 'createDate': '1/7/2021 8:34:22 PM', 'createdBy': 'Intelygenz Ai', 'creationNote': None, 'resolveDate': '1/7/2021 10:58:55 PM', 'resolvedby': None, 'closeDate': None, 'closedBy': None, 'lastUpdate': None, 'updatedBy': None, 'mostRecentNote': '1/7/2021 8:54:47 PM Intelygenz Ai', 'nextScheduledDate': '1/14/2021 5:00:00 AM', 'flags': '', 'severity': '3'}  # noqa


@pytest.fixture(scope='function')
def ticket_details_1():
    return {
        'ticketDetails': [{'detailID': 5583073, 'detailType': 'Repair_WTN', 'detailStatus': 'C', 'detailValue': 'VC05200085762', 'assignedToName': '0', 'currentTaskID': None, 'currentTaskName': None, 'lastUpdatedBy': 385677, 'lastUpdatedAt': '2021-01-07T17:59:12.523-05:00'}],  # noqa
        'ticketNotes': [{'noteId': 77127141, 'noteValue': '1/7/2021 3:34:01 PM\n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:34:04.057-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77127156, 'noteValue': '#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-07 15:33:44.229001-05:00 \nThroughput (Receive): 9262.009 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:34:26.48-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77127877, 'noteValue': 'Links\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | Bandwidth\tPre-Notifications\tAlerts\tSignal\tLatency\tJitter\tPacket Loss\t\nComcast Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t231.36 kbps27.15 Mbps\n20.47 Mbps189.21 Mbps\tEdit\tEdit\tn/a\t18 msec\n9 msec\t0 msec\n0 msec\t0.00%\n0.00%\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t5.83 Mbps9.94 Mbps\n9.32 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t9 msec\n11 msec\t0 msec\n0 msec\t0.00%\n0.00%\t', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:49:19.41-05:00', 'creator': 'hchauhan@mettel.net'}, {'noteId': 77128120, 'noteValue': 'Unresolve Action: Holmdel NOC Investigate ', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:54:43.647-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77128126, 'noteValue': '#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-07 15:54:08.913048-05:00 \nThroughput (Receive): 9274.063 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 90% (8903.7 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n\nTimeStamp: 2021-01-07 15:54:44.279607-05:00', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-07T15:54:47.443-05:00', 'creator': 'api_1@bruin.com'}]  # noqa
    }


@pytest.fixture(scope='function')
def ticket_2():
    return {'clientID': 83109, 'clientName': 'RSI', 'ticketID': 5075176, 'category': 'SD-WAN', 'topic': 'Service Affecting Trouble', 'referenceTicketNumber': 0, 'ticketStatus': 'Closed', 'address': {'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714', 'country': 'USA'}, 'createDate': '1/5/2021 9:22:11 PM', 'createdBy': 'Intelygenz Ai', 'creationNote': None, 'resolveDate': '1/6/2021 10:34:51 PM', 'resolvedby': None, 'closeDate': None, 'closedBy': None, 'lastUpdate': None, 'updatedBy': None, 'mostRecentNote': '1/6/2021 1:58:04 PM Intelygenz Ai', 'nextScheduledDate': '1/12/2021 5:00:00 AM', 'flags': '', 'severity': '3'}  # noqa


@pytest.fixture(scope='function')
def ticket_details_2():
    return {
        'ticketDetails': [{'detailID': 5576149, 'detailType': 'Repair_WTN', 'detailStatus': 'C', 'detailValue': 'VC05200085762', 'assignedToName': '0', 'currentTaskID': None, 'currentTaskName': None, 'lastUpdatedBy': 385677, 'lastUpdatedAt': '2021-01-06T17:35:10.317-05:00'}],  # noqa
        'ticketNotes': [{'noteId': 77051076, 'noteValue': '1/5/2021 4:22:09 PM\n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T16:22:11.247-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77051080, 'noteValue': '#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-05 16:22:09.661410-05:00 \nThroughput (Receive): 8150.85 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T16:22:24.03-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77076710, 'noteValue': 'Unresolve Action: Holmdel NOC Investigate ', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-06T08:57:35.85-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77076719, 'noteValue': '#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \nThroughput (Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-06T08:58:04.083-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77076720, 'noteValue': '#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-06 08:57:09.372295-05:00 \nThroughput (Receive): 9196.147 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n\nTimeStamp: 2021-01-06 08:57:36.651254-05:00', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-06T08:58:04.177-05:00', 'creator': 'api_1@bruin.com'}]  # noqa
    }


@pytest.fixture(scope='function')
def ticket_3():
    return {'clientID': 83109, 'clientName': 'RSI', 'ticketID': 5074441, 'category': 'SD-WAN', 'topic': 'Service Affecting Trouble', 'referenceTicketNumber': 0, 'ticketStatus': 'Closed', 'address': {'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714', 'country': 'USA'}, 'createDate': '1/5/2021 6:49:25 PM', 'createdBy': 'Intelygenz Ai', 'creationNote': None, 'resolveDate': '1/5/2021 7:34:09 PM', 'resolvedby': None, 'closeDate': None, 'closedBy': None, 'lastUpdate': None, 'updatedBy': None, 'mostRecentNote': '1/5/2021 7:33:34 PM Dhruv Patel', 'nextScheduledDate': '1/12/2021 5:00:00 AM', 'flags': '', 'severity': '3'}  # noqa


@pytest.fixture(scope='function')
def ticket_details_3():
    return {
        'ticketDetails': [{'detailID': 5575534, 'detailType': 'Repair_WTN', 'detailStatus': 'C', 'detailValue': 'VC05200085762', 'assignedToName': '0', 'currentTaskID': None, 'currentTaskName': None, 'lastUpdatedBy': 385676, 'lastUpdatedAt': '2021-01-05T14:34:23.72-05:00'}],  # noqa
        'ticketNotes': [{'noteId': 77043435, 'noteValue': '1/5/2021 1:49:21 PM\n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T13:49:25.337-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77043439, 'noteValue': '#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-05 13:49:21.416728-05:00 \nThroughput (Receive): 8271.982 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T13:49:27.65-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77045257, 'noteValue': 'BW utilization is normal compared to BYOB ckt.\nLink is stable.\n\nLinks\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | Bandwidth\tPre-Notifications\tAlerts\tSignal\t\nComcast Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t1.95 Mbps27.15 Mbps\n6.11 Mbps189.21 Mbps\tEdit\tEdit\tn/a\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t3.02 Mbps9.94 Mbps\n1.45 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t\n \n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T14:33:34.623-05:00', 'creator': 'dpatel@mettel.net'}]  # noqa
    }


@pytest.fixture(scope='function')
def ticket_4():
    return {'clientID': 83109, 'clientName': 'RSI', 'ticketID': 5073652, 'category': 'SD-WAN', 'topic': 'Service Affecting Trouble', 'referenceTicketNumber': 0, 'ticketStatus': 'Closed', 'address': {'address': '621 Hill Ave', 'city': 'Nashville', 'state': 'TN', 'zip': '37210-4714', 'country': 'USA'}, 'createDate': '1/5/2021 3:29:39 PM', 'createdBy': 'Intelygenz Ai', 'creationNote': None, 'resolveDate': '1/5/2021 5:06:54 PM', 'resolvedby': None, 'closeDate': None, 'closedBy': None, 'lastUpdate': None, 'updatedBy': None, 'mostRecentNote': '1/5/2021 4:52:05 PM Intelygenz Ai', 'nextScheduledDate': '1/12/2021 5:00:00 AM', 'flags': '', 'severity': '3'}  # noqa


@pytest.fixture(scope='function')
def ticket_details_4():
    return {
        'ticketDetails': [{'detailID': 5574754, 'detailType': 'Repair_WTN', 'detailStatus': 'C', 'detailValue': 'VC05200085762', 'assignedToName': '0', 'currentTaskID': None, 'currentTaskName': None, 'lastUpdatedBy': 385676, 'lastUpdatedAt': '2021-01-05T12:07:31.707-05:00'}],  # noqa
        'ticketNotes': [{'noteId': 77034430, 'noteValue': '1/5/2021 10:29:37 AM\n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T10:29:38.857-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77034460, 'noteValue': '#*Automation Engine*# \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-05 10:29:22.043598-05:00 \nThroughput (Receive): 8365.164 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T10:30:21.64-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77034984, 'noteValue': 'Bandwidth utilization is nothing compared to BYOB ckt.\n\nLinks\tCloud Status\tVPN Status\tInterface (WAN Type)\tThroughput | Bandwidth\tPre-Notifications\tAlerts\tSignal\t\nComcast Cable (BYOB) \n173.10.211.109\t\t\tGE2 (Ethernet)\t1.81 Mbps27.15 Mbps\n6.91 Mbps189.21 Mbps\tEdit\tEdit\tn/a\t\nApex 10M (MetTel CID: BBT.113719) \n32.140.174.242\t\t\tGE1 (Ethernet)\t428.21 kbps9.94 Mbps\n6.59 Mbps9.89 Mbps\tEdit\tEdit\tn/a\t\n \nLink is stable.', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T10:39:43.817-05:00', 'creator': 'dpatel@mettel.net'}, {'noteId': 77039079, 'noteValue': 'Unresolve Action: Holmdel NOC Investigate ', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T11:52:05.01-05:00', 'creator': 'api_1@bruin.com'}, {'noteId': 77039080, 'noteValue': '#*Automation Engine*#\nRe-opening ticket.\n \nEdge Name: TN-NASH-4840-HC-DI \nTrouble: Bandwidth Over Utilization \nInterface: GE1 \nName: Apex 10M (MetTel CID: BBT.113719) \nInterval for Scan: 20 \nScan Time: 2021-01-05 11:51:39.347045-05:00 \nThroughput (Receive): 8139.369 Kbps \nBandwidth (Receive): 9893.0 Kbps \nThreshold (Receive): 80% (7914.4 Kbps) \nLinks:  [Edge|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/]  -  [QoE|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/qoe/]  -  [Transport|https://metvco03.mettel.net/#!/operator/customer/124/monitor/edge/2044/links/]  \n \n\nTimeStamp: 2021-01-05 11:52:05.664662-05:00', 'serviceNumber': ['VC05200085762'], 'createdDate': '2021-01-05T11:52:05.603-05:00', 'creator': 'api_1@bruin.com'}]  # noqa
    }


@pytest.fixture(scope='function')
def response_bruin_with_all_tickets_without_details(ticket_1, ticket_2, ticket_3, ticket_4):
    return {
        'body': [ticket_1, ticket_2, ticket_3, ticket_4],
        'status': 200
    }


@pytest.fixture(scope='function')
def response_bruin_with_no_tickets():
    return {
        'body': [],
        'status': 200
    }


@pytest.fixture(scope='function')
def response_bruin_401():
    return {
        'body': "error 401",
        'status': 401
    }


@pytest.fixture(scope='function')
def response_bruin_403():
    return {
        'body': "error 403",
        'status': 403
    }


@pytest.fixture(scope='function')
def response_bruin_with_error():
    return {
        'body': "Some error",
        'status': 400
    }


@pytest.fixture(scope='function')
def response_bruin_with_all_tickets(ticket_1, ticket_details_1, ticket_2, ticket_details_2, ticket_3, ticket_details_3,
                                    ticket_4, ticket_details_4):
    return {
        ticket_1['ticketID']: {
            "ticket": ticket_1,
            "ticket_details": ticket_details_1
        },
        ticket_2['ticketID']: {
            "ticket": ticket_2,
            "ticket_details": ticket_details_2
        },
        ticket_3['ticketID']: {
            "ticket": ticket_3,
            "ticket_details": ticket_details_3
        },
        ticket_4['ticketID']: {
            "ticket": ticket_4,
            "ticket_details": ticket_details_4
        }
    }


@pytest.fixture(scope='function')
def response_bruin_with_all_tickets_with_exception():
    return None


@pytest.fixture(scope='function')
def response_mapped_tickets(ticket_1, ticket_details_1, ticket_2, ticket_details_2, ticket_3, ticket_details_3,
                            ticket_4, ticket_details_4):
    ret = defaultdict(list)
    ret[ticket_details_1['ticketDetails'][0]['detailValue']].append({
        'ticket': ticket_1,
        'ticket_details': ticket_details_1
    })
    ret[ticket_details_2['ticketDetails'][0]['detailValue']].append({
        'ticket': ticket_2,
        'ticket_details': ticket_details_2
    })
    ret[ticket_details_3['ticketDetails'][0]['detailValue']].append({
        'ticket': ticket_3,
        'ticket_details': ticket_details_3
    })
    ret[ticket_details_4['ticketDetails'][0]['detailValue']].append({
        'ticket': ticket_4,
        'ticket_details': ticket_details_4
    })
    return ret


@pytest.fixture(scope='function')
def response_prepare_items_for_report(ticket_1, ticket_2, ticket_3, ticket_4, ticket_details_1):
    return [
        {
            "customer": {
                "client_id": ticket_1['clientID'],
                "client_name": "RSI"
            },
            "location": ticket_1['address'],
            "serial_number": ticket_details_1['ticketDetails'][0]['detailValue'],
            "number_of_tickets": 4,
            "bruin_tickets_id": [
                ticket_1['ticketID'],
                ticket_2['ticketID'],
                ticket_3['ticketID'],
                ticket_4['ticketID']
            ]
        }
    ]
