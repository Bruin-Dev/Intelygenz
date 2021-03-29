# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os

ENVIRONMENT_ID = os.environ['ENVIRONMENT_SLUG']
BRANCH_NAME = os.environ['CI_COMMIT_REF_NAME']
PAPERTRAIL_PORT = os.environ['TF_VAR_PAPERTRAIL_PORT']
PAPERTRAIL_CLI_VERSION = os.environ['PAPERTRAIL_CLI_VERSION']
PAPERTRAIL_CLI_DONWLOAD_URL = f"https://github.com/xoanmm/go-papertrail-cli/releases/download/v" \
                              f"{PAPERTRAIL_CLI_VERSION}/go-papertrail-cli_{PAPERTRAIL_CLI_VERSION}" \
                              f"_linux_64-bit.tar.gz"
SYSTEM_IPS = "*"

if BRANCH_NAME == "master":
    ENVIRONMENT_ID = "master"
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
                    "query": f"bruin-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[bruin-bridge] - logs",
                    "repository": "automation-bruin-bridge"
                },
                {
                    "query": f"cts-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[cts-bridge] - logs",
                    "repository": "automation-cts-bridge"
                },
                {
                    "query": f"customer-cache AND {ENVIRONMENT_ID} AND <BUILD_NUMBER> AND -\"-customer-cache\"",
                    "search_name": f"[customer-cache] - logs",
                    "repository": "automation-customer-cache"
                },
                {
                    "query": f"dispatch-portal-backend AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[dispatch-portal-backend] - logs",
                    "repository": "automation-dispatch-portal-backend"
                },
                {
                    "query": f"grafana AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[grafana] - logs",
                    "repository": "automation-metrics-dashboard/grafana"
                },
                {
                    "query": f"hawkeye-affecting-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-affecting-monitor] - logs",
                    "repository": "automation-hawkeye-affecting-monitor"
                },
                {
                    "query": f"hawkeye-customer-cache AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-customer-cache] - logs",
                    "repository": "automation-hawkeye-customer-cache"
                },
                {
                    "query": f"hawkeye-outage-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-outage-monitor] - logs",
                    "repository": "automation-hawkeye-outage-monitor"
                },
                {
                    "query": f"intermapper-outage-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-outage-monitor] - logs",
                    "repository": "automation-intermapper-outage-monitor"
                },
                {
                    "query": f"last-contact-report AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[last-contact-report] - logs",
                    "repository": "automation-last-contact-report"
                },
                {
                    "query": f"lit-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[lit-bridge] - logs",
                    "repository": "automation-lit-bridge"
                },
                {
                    "query": f"lumin-billing-report AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[lumin-billing-report] - logs",
                    "repository": "automation-lumin-billing-report"
                },
                {
                    "query": f"hawkeye-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[hawkeye-bridge] - logs",
                    "repository": "automation-hawkeye-bridge"
                },
                {
                    "query": f"NGINX AND <BUILD_NUMBER> AND {ENVIRONMENT_ID}",
                    "search_name": f"[nginx] - logs",
                    "repository": "automation-dispatch-portal-frontend/nginx"
                },
                {
                    "query": f"service-affecting-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-affecting-monitor] - logs",
                    "repository": "automation-service-affecting-monitor"
                },
                {
                    "query": f"service-dispatch-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-dispatch-monitor] - logs",
                    "repository": "automation-service-dispatch-monitor"
                },
                {
                    "query": f"service-outage-monitor-1 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-1] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-2 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-2] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-3 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-3] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-4 AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-4] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"service-outage-monitor-triage AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[service-outage-monitor-triage] - logs",
                    "repository": "automation-service-outage-monitor"
                },
                {
                    "query": f"sites-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[sites-monitor] - logs",
                    "repository": "automation-sites-monitor"
                },
                {
                    "query": f"t7-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[t7-bridge] - logs",
                    "repository": "automation-t7-bridge"
                },
                {
                    "query": f"tnba-monitor AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-monitor] - logs",
                    "repository": "automation-tnba-monitor"
                },
                {
                    "query": f"tnba-feedback AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[tnba-feedback] - logs",
                    "repository": "automation-tnba-feedback"
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_ID} AND <BUILD_NUMBER>",
                    "search_name": f"[velocloud-bridge] - logs",
                    "repository": "automation-velocloud-bridge"
                },
                {
                    "query": f"{ENVIRONMENT_ID}",
                    "search_name": f"[all modules] - logs",
                }
            ]
        },
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} notifications",
            "notifications": True,
            "searches": [
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Successfully created outage ticket for edge\"",
                    "search_name": f"[service-outage-monitor] - ticket creation"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Ticket linked to edge was autoresolved!\"",
                    "search_name": f"[service-outage-monitor] - ticked autoresolved"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Triage appended to detail\"",
                    "search_name": f"[service-outage-monitor] - triage appended"
                }
            ]
        },
        {
            "wildcard": f"{SYSTEM_IPS}",
            "destination_port": f"{PAPERTRAIL_PORT}",
            "system_type": "hostname",
            "group_name": f"[{ENVIRONMENT_NAME}] - {BRANCH_NAME} alarms",
            "alarms": True,
            "searches": [
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"Successfully created outage ticket for edge\"",
                    "search_name": f"[service-outage-monitor] - ticket creation"
                },
                {
                    "query": f"velocloud-bridge AND {ENVIRONMENT_ID} AND "
                             f"\"ERROR:\"",
                    "search_name": f"[velocloud-bridge] - ERROR messages"
                },
                {
                    "query": f"bruin-bridge AND {ENVIRONMENT_ID} AND "
                             f"\"ERROR:\"",
                    "search_name": f"[bruin-bridge] - ERROR messages"
                },
                {
                    "query": f"service-outage-monitor AND {ENVIRONMENT_ID} AND "
                             f"\"ERROR:\"",
                    "search_name": f"[service-outage-monitor] - ERROR messages"
                }
            ]
        }
    ]
}
