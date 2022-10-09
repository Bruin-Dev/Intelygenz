# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os

ENVIRONMENT_ID = os.environ["ENVIRONMENT_SLUG"]
BRANCH_NAME = os.environ["CI_COMMIT_REF_NAME"]
PAPERTRAIL_PORT = os.environ["PAPERTRAIL_PORT"]
PAPERTRAIL_CLI_VERSION = os.environ["PAPERTRAIL_CLI_VERSION"]
PAPERTRAIL_CLI_DONWLOAD_URL = (
    f"https://github.com/xoanmm/go-papertrail-cli/releases/download/v"
    f"{PAPERTRAIL_CLI_VERSION}/go-papertrail-cli_{PAPERTRAIL_CLI_VERSION}"
    f"_linux_64-bit.tar.gz"
)
SYSTEM_IPS = "*"

if BRANCH_NAME == "master":
    ENVIRONMENT_NAME = "production"
else:
    ENVIRONMENT_NAME = ENVIRONMENT_ID


PAPERTRAIL_PROVISIONING = {
    "groups": [
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} logs",
            "searches": [
                {
                    "query": f"bruin-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[bruin-bridge] - logs",
                    "repository": "bruin-bridge",
                },
                {
                    "query": f'customer-cache AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER> AND -"-customer-cache"',
                    "search_name": f"[customer-cache] - logs",
                    "repository": "customer-cache",
                },
                {
                    "query": f"digi-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[digi-bridge] - logs",
                    "repository": "digi-bridge",
                },
                {
                    "query": f"digi-reboot-report AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[digi-reboot-report] - logs",
                    "repository": "digi-reboot-report",
                },
                {
                    "query": f"dri-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[dri-bridge] - logs",
                    "repository": "dri-bridge",
                },
                # {
                #     "query": f"grafana AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                #     "search_name": f"[grafana] - logs",
                #     "repository": "metrics-dashboard/grafana"
                # },
                {
                    "query": f"email-tagger-kre-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[email-tagger-kre-bridge] - logs",
                    "repository": "email-tagger-kre-bridge",
                },
                {
                    "query": f"email-tagger-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[email-tagger-monitor] - logs",
                    "repository": "email-tagger-monitor",
                },
                {
                    "query": f"fraud-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[fraud-monitor] - logs",
                    "repository": "fraud-monitor",
                },
                {
                    "query": f"forticloud-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[forticloud-monitor] - logs",
                    "repository": "forticloud-monitor",
                },
                {
                    "query": f"forticloud-poller AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[forticloud-poller] - logs",
                    "repository": "forticloud-poller",
                },
                {
                    "query": f"forticloud-cache AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[forticloud-cache] - logs",
                    "repository": "forticloud-cache",
                },
                {
                    "query": f"gateway-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[gateway-monitor] - logs",
                    "repository": "gateway-monitor",
                },
                {
                    "query": f"hawkeye-affecting-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-affecting-monitor] - logs",
                    "repository": "hawkeye-affecting-monitor",
                },
                {
                    "query": f"hawkeye-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-bridge] - logs",
                    "repository": "hawkeye-bridge",
                },
                {
                    "query": f"hawkeye-customer-cache AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-customer-cache] - logs",
                    "repository": "hawkeye-customer-cache",
                },
                {
                    "query": f"hawkeye-outage-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-outage-monitor] - logs",
                    "repository": "hawkeye-outage-monitor",
                },
                {
                    "query": f"intermapper-outage-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[intermapper-outage-monitor] - logs",
                    "repository": "intermapper-outage-monitor",
                },
                {
                    "query": f"last-contact-report AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[last-contact-report] - logs",
                    "repository": "last-contact-report",
                },
                {
                    "query": f"links-metrics-api AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[links-metrics-api] - logs",
                    "repository": "links-metrics-api",
                },
                {
                    "query": f"links-metrics-collector AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[links-metrics-collector] - logs",
                    "repository": "links-metrics-collector",
                },
                {
                    "query": f"lumin-billing-report AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[lumin-billing-report] - logs",
                    "repository": "lumin-billing-report",
                },
                {
                    "query": f"email-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[email-bridge] - logs",
                    "repository": "email-bridge",
                },
                {
                    "query": f"notifications-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[notifications-bridge] - logs",
                    "repository": "notifications-bridge",
                },
                {
                    "query": f"repair-tickets-kre-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[repair-tickets-kre-bridge] - logs",
                    "repository": "repair-tickets-kre-bridge",
                },
                {
                    "query": f"repair-tickets-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[repair-tickets-monitor] - logs",
                    "repository": "repair-tickets-monitor",
                },
                {
                    "query": f"NGINX AND <BUILD_NUMBER> AND {ENVIRONMENT_NAME}",
                    "search_name": f"[nginx] - logs",
                    "repository": "dispatch-portal-frontend/nginx",
                },
                {
                    "query": f"sam-met AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[service-affecting-monitor] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-mettel-velocloud-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-vco01] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-metvco02-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-vco02] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-metvco03-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-vco03] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-metvco04-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-vco04] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"som-met AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-mettel-velocloud-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-vco01] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-metvco02-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-vco02] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-metvco03-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-vco03] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-metvco04-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-vco04] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"service-outage-monitor-triage AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-triage] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"servicenow-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[servicenow-bridge] - logs",
                    "repository": "servicenow-bridge",
                },
                {
                    "query": f"t7-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[t7-bridge] - logs",
                    "repository": "t7-bridge",
                },
                {
                    "query": f"task-dispatcher AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[task-dispatcher] - logs",
                    "repository": "task-dispatcher",
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-feedback] - logs",
                    "repository": "tnba-feedback",
                },
                {
                    "query": f"tnba-met AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-monitor] - logs",
                    "repository": "tnba-monitor",
                },
                {
                    "query": f"tnba-mettel-velocloud-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-vco01] - logs",
                    "repository": "tnba-monitor",
                },
                {
                    "query": f"tnba-metvco02-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-vco02] - logs",
                    "repository": "tnba-monitor",
                },
                {
                    "query": f"tnba-metvco03-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-vco03] - logs",
                    "repository": "tnba-monitor",
                },
                {
                    "query": f"tnba-metvco04-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-vco04] - logs",
                    "repository": "tnba-monitor",
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[velocloud-bridge] - logs",
                    "repository": "velocloud-bridge",
                },
                {
                    "query": f"{ENVIRONMENT_NAME}",
                    "search_name": f"[all modules] - logs",
                },
            ],
        },
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} notifications",
            "notifications": True,
            "searches": [
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Successfully created outage ticket for edge"',
                    "search_name": f"[service-outage-monitor] - ticket creation",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Ticket linked to edge was autoresolved!"',
                    "search_name": f"[service-outage-monitor] - ticked autoresolved",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND Triage appended to detail",
                    "search_name": f"[service-outage-monitor] - triage appended",
                },
            ],
        },
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} alarms",
            "alarms": True,
            "searches": [
                {
                    "query": f"bruin-bridge AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[bruin-bridge] - ERROR messages",
                },
                {
                    "query": f"email-tagger-monitor AND {ENVIRONMENT_ID} AND "
                    f'"An error occurred when sending emails to Email Tagger"',
                    "search_name": "[email-tagger-monitor] KRE communication error",
                },
                {
                    "query": f"forticloud-cache AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[forticloud-cache] - ERROR messages",
                },
                {
                    "query": f"gateway-monitor AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[gateway-monitor] - ERROR messages",
                },
                {
                    "query": f"forticloud-poller AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[forticloud-poller] - ERROR messages",
                },
                {
                    "query": f"task-dispatcher AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[task-dispatcher] - ERROR messages",
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_ID} AND An error occurred when posting metrics",
                    "search_name": f"[tnba-feedback] Search Error saving metrics",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND "
                    f'"Error while claiming T7 prediction for ticket"',
                    "search_name": f"[tnba-monitor] GRPC communication error with KRE",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND An error occurred when posting live metrics",
                    "search_name": f"[tnba-monitor] Error posting live automation metrics",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND ERROR:",
                    "search_name": f"[service-outage-monitor] - ERROR messages",
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_ID} AND An error occurred when posting metrics",
                    "search_name": f"[tnba-feedback] Search Error saving metrics",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND "
                    f'"Error while claiming T7 prediction for ticket"',
                    "search_name": f"[tnba-monitor] GRPC communication error with KRE",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND An error occurred when posting live metrics",
                    "search_name": f"[tnba-monitor] Error posting live automation metrics",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND ERROR:",
                    "search_name": f"[service-outage-monitor] - ERROR messages",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Successfully created outage ticket for edge"',
                    "search_name": f"[service-outage-monitor] - ticket creation",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND Triage process finished!",
                    "search_name": f"[triage] Triage finished",
                },
                {
                    "query": f"servicenow-bridge AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[servicenow-bridge] - ERROR messages",
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_NAME} AND ERROR:",
                    "search_name": f"[velocloud-bridge] - ERROR messages",
                },
                {
                    "query": f"intermapper-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Received the following from the gmail account mettel.automation@intelygenz.com: []"',
                    "search_name": f"[intermapper-outage-monitor] - Not receiving emails",
                },
            ],
        },
    ]
}
