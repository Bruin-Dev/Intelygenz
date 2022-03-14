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
                    "query": f"notifier AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[notifier] - logs",
                    "repository": "notifier",
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
                    "query": f"sam-mettel-velocloud-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-mettel-velocloud-net] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-metvco02-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-metvco02-mettel-net] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-metvco03-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-metvco03-mettel-net] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"sam-metvco04-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sam-metvco04-mettel-net] - logs",
                    "repository": "service-affecting-monitor",
                },
                {
                    "query": f"som-mettel-velocloud-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-mettel-velocloud-net] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-metvco02-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-metvco02-mettel-net] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-metvco03-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-metvco03-mettel-net] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"som-metvco04-mettel-net AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[som-metvco04-mettel-net] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"service-outage-monitor-triage AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-triage] - logs",
                    "repository": "service-outage-monitor",
                },
                {
                    "query": f"sites-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[sites-monitor] - logs",
                    "repository": "sites-monitor",
                },
                {
                    "query": f"t7-bridge AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[t7-bridge] - logs",
                    "repository": "t7-bridge",
                },
                {
                    "query": f"ticket-collector AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[ticket-collector] - logs",
                    "repository": "ticket-collector",
                },
                {
                    "query": f"ticket-statistics AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[ticket-statistics] - logs",
                    "repository": "ticket-statistics",
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-feedback] - logs",
                    "repository": "tnba-feedback",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_NAME} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-monitor] - logs",
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
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Triage appended to detail"',
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
                    "query": f"bruin-bridge AND {ENVIRONMENT_NAME} AND " f'"ERROR:"',
                    "search_name": f"[bruin-bridge] - ERROR messages",
                },
                {
                    "query": f"email-tagger-monitor AND {ENVIRONMENT_ID} AND "
                    f'"An error occurred when sending emails to Email Tagger"',
                    "search_name": "[email-tagger-monitor] KRE communication error",
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_ID} AND "
                    f'"An error occurred when posting metrics"',
                    "search_name": f"[tnba-feedback] Search Error saving metrics",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND "
                    f'"Error while claiming T7 prediction for ticket"',
                    "search_name": f"[tnba-monitor] GRPC communication error with KRE",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND "
                    f'"An error occurred when posting live metrics"',
                    "search_name": f"[tnba-monitor] Error posting live automation metrics",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                    f'"ERROR:"',
                    "search_name": f"[service-outage-monitor] - ERROR messages",
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_ID} AND "
                    f'"An error occurred when posting metrics"',
                    "search_name": f"[tnba-feedback] Search Error saving metrics",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND "
                    f'"Error while claiming T7 prediction for ticket"',
                    "search_name": f"[tnba-monitor] GRPC communication error with KRE",
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND "
                    f'"An error occurred when posting live metrics"',
                    "search_name": f"[tnba-monitor] Error posting live automation metrics",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                    f'"ERROR:"',
                    "search_name": f"[service-outage-monitor] - ERROR messages",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Successfully created outage ticket for edge"',
                    "search_name": f"[service-outage-monitor] - ticket creation",
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_NAME} AND "
                    f'"Triage process finished!"',
                    "search_name": f"[triage] Triage finished",
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_NAME} AND "
                    f'"ERROR:"',
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
