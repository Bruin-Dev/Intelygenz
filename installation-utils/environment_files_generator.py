# Note: Please ignore "line too long" warnings in this file

import argparse
import getpass
import json
import os

import boto3


def set_parameter(local_dict, keys, value):
    for key in keys[:-1]:
        local_dict = local_dict.setdefault(key, {})
    local_dict[keys[-1]] = value


parser = argparse.ArgumentParser()
parser.add_argument("--aws-profile", default="ops-mettel")
aws_profile = parser.parse_args().aws_profile

session = boto3.Session(profile_name=aws_profile)
ssm = session.client("ssm")
paginator = ssm.get_paginator("get_parameters_by_path")
response_iterator = paginator.paginate(Path="/automation-engine", Recursive=True, WithDecryption=True)

parameters = {}

print("Getting parameters from AWS")
for response in response_iterator:
    for parameter in response["Parameters"]:
        name = parameter["Name"].replace("/automation-engine/", "")
        set_parameter(parameters, name.split("/"), parameter["Value"])
print("Finished getting parameters")

# Shared variables
ENVIRONMENT_NAME = getpass.getuser() + "-local"
CURRENT_ENVIRONMENT = "local"
TIMEZONE = parameters["common"]["timezone"]
IPA_SYSTEM_USERNAME_IN_BRUIN = parameters["common"]["bruin-ipa-system-username"]
AUTORESOLVE_DAY_START_HOUR = parameters["common"]["autoresolve-day-start-hour"]
AUTORESOLVE_DAY_END_HOUR = parameters["common"]["autoresolve-day-end-hour"]
LINK_LABELS_BLACKLISTED_FROM_ASR_FORWARDS = json.dumps(json.loads(parameters["common"]["link-labels-blacklisted-from-asr-forwards"]))
LINK_LABELS_BLACKLISTED_FROM_HNOC_FORWARDS = json.dumps(json.loads(parameters["common"]["link-labels-blacklisted-from-hnoc-forwards"]))

# Metrics variables
METRICS_RELEVANT_CLIENTS = parameters["common"]["metrics"]["relevant-clients"]

# We should use DEV variables here, but their test inventories lack lots of data so it's not worth it
# Bruin Bridge variables
BRUIN_CLIENT_ID = parameters["pro"]["bruin-bridge"]["client-id"]
BRUIN_CLIENT_SECRET = parameters["pro"]["bruin-bridge"]["client-secret"]
BRUIN_LOGIN_URL = parameters["pro"]["bruin-bridge"]["login-url"]
BRUIN_BASE_URL = parameters["pro"]["bruin-bridge"]["base-url"]

# Customer Cache variables
CUSTOMER_CACHE__VELOCLOUD_HOSTS = parameters["dev"]["customer-cache"]["velocloud-hosts"]
CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT = parameters["dev"]["customer-cache"]["duplicate-inventories-recipient"]
CUSTOMER_CACHE__REFRESH_JOB_INTERVAL = parameters["common"]["customer-cache"]["refresh-job-interval"]
CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL = parameters["common"]["customer-cache"]["refresh-check-interval"]
CUSTOMER_CACHE__BLACKLISTED_EDGES = parameters["dev"]["customer-cache"]["blacklisted-edges"]
CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS = parameters["dev"]["customer-cache"]["blacklisted-clients-with-pending-status"]
CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES = parameters["common"]["customer-cache"]["whitelisted-management-statuses"]

# DRI variables
DRI_BRIDGE__USERNAME = parameters["common"]["dri-bridge"]["username"]
DRI_BRIDGE__PASSWORD = parameters["common"]["dri-bridge"]["password"]
DRI_BRIDGE__BASE_URL = parameters["common"]["dri-bridge"]["base-url"]
DRI_BRIDGE__DRI_DATA_REDIS_TTL = parameters["common"]["dri-bridge"]["dri-data-redis-ttl"]

# The DEV environment is not exposed to the world, so it's only accessible from ephemeral environments
# Local environments can only access PRO
# DiGi variables
DIGI_CLIENT_ID = parameters["pro"]["digi-bridge"]["digi-reboot-api-client-id"]
DIGI_CLIENT_SECRET = parameters["pro"]["digi-bridge"]["digi-reboot-api-client-secret"]
DIGI_BASE_URL = parameters["pro"]["digi-bridge"]["digi-reboot-api-base-url"]
DIGI_TOKEN_TTL = parameters["common"]["digi-bridge"]["digi-reboot-api-token-ttl"]
DIGI_HEADERS = parameters["common"]["digi-bridge"]["digi-headers"]

# DiGi Reboot Report variables
DIGI_REBOOT_REPORT__JOB_INTERVAL = parameters["common"]["digi-reboot-report"]["report-job-interval"]
DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL = parameters["common"]["digi-reboot-report"]["logs-lookup-interval"]
DIGI_REBOOT_REPORT__RECIPIENT = parameters["dev"]["digi-reboot-report"]["report-recipient"]

# Forticloud variables
FORTICLOUD_BASE_URL = parameters["dev"]["forticloud"]["base-url"]
FORTICLOUD_USERNAME = parameters["common"]["forticloud"]["username"]
FORTICLOUD_PASSWORD = parameters["common"]["forticloud"]["password"]
FORTICLOUD_ACCOUNT = parameters["common"]["forticloud"]["account"]

# Fraud Monitor variables
FRAUD_MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["fraud-monitor"]["monitoring-job-interval"]
FRAUD_MONITOR__OBSERVED_INBOX_EMAIL_ADDRESS = parameters["dev"]["fraud-monitor"]["observed-inbox-email-address"]
FRAUD_MONITOR__OBSERVED_INBOX_SENDERS = json.dumps(json.loads(parameters["common"]["fraud-monitor"]["observed-inbox-senders"]))
FRAUD_MONITOR__DEFAULT_CONTACT_FOR_NEW_TICKETS = json.dumps(json.loads(parameters["common"]["fraud-monitor"]["default-contact-for-new-tickets"]))
FRAUD_MONITOR__DEFAULT_CLIENT_INFO_FOR_DID_WITHOUT_INVENTORY = json.dumps(json.loads(parameters["common"]["fraud-monitor"]["default-client-info-for-did-without-inventory"]))
FRAUD_MONITOR__ALERTS_LOOKUP_DAYS = parameters["common"]["fraud-monitor"]["alerts-lookup-days"]

# Hawkeye Affecting Monitor variables
HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["hawkeye-affecting-monitor"]["monitoring-job-interval"]
HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL = parameters["common"]["hawkeye-affecting-monitor"]["probes-tests-results-lookup-interval"]
HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY = parameters["common"]["hawkeye-affecting-monitor"]["monitored-product-category"]

# Hawkeye Bridge variables
HAWKEYE_BRIDGE__CLIENT_USERNAME = parameters["common"]["hawkeye-bridge"]["client-username"]
HAWKEYE_BRIDGE__CLIENT_PASSWORD = parameters["common"]["hawkeye-bridge"]["client-password"]
HAWKEYE_BRIDGE__BASE_URL = parameters["common"]["hawkeye-bridge"]["base-url"]

# Hawkeye Customer Cache variables
HAWKEYE_CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT = parameters["dev"]["hawkeye-customer-cache"]["duplicate-inventories-recipient"]
HAWKEYE_CUSTOMER_CACHE__REFRESH_JOB_INTERVAL = parameters["common"]["hawkeye-customer-cache"]["refresh-job-interval"]
HAWKEYE_CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES = parameters["common"]["hawkeye-customer-cache"]["whitelisted-management-statuses"]

# Hawkeye Outage Monitor variables
HAWKEYE_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["hawkeye-outage-monitor"]["monitoring-job-interval"]
HAWKEYE_OUTAGE_MONITOR__QUARANTINE_FOR_DEVICES_IN_OUTAGE = parameters["common"]["hawkeye-outage-monitor"]["quarantine-for-devices-in-outage"]
HAWKEYE_OUTAGE_MONITOR__MONITORED_PRODUCT_CATEGORY = parameters["common"]["hawkeye-outage-monitor"]["monitored-product-category"]
HAWKEYE_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE = parameters["common"]["hawkeye-outage-monitor"]["grace-period-to-autoresolve-after-last-documented-outage"]

# InterMapper Outage Monitor variables
INTERMAPPER_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["intermapper-outage-monitor"]["monitoring-job-interval"]
INTERMAPPER_OUTAGE_MONITOR__OBSERVED_INBOX_EMAIL_ADDRESS = parameters["dev"]["intermapper-outage-monitor"]["observed-inbox-email-address"]
INTERMAPPER_OUTAGE_MONITOR__OBSERVED_INBOX_SENDERS = json.dumps(json.loads(parameters["common"]["intermapper-outage-monitor"]["observed-inbox-senders"]))
INTERMAPPER_OUTAGE_MONITOR__MONITORED_DOWN_EVENTS = json.dumps(json.loads(parameters["common"]["intermapper-outage-monitor"]["monitored-down-events"]))
INTERMAPPER_OUTAGE_MONITOR__MONITORED_UP_EVENTS = json.dumps(json.loads(parameters["common"]["intermapper-outage-monitor"]["monitored-up-events"]))
INTERMAPPER_OUTAGE_MONITOR__MAX_AUTORESOLVES_PER_TICKET = parameters["common"]["intermapper-outage-monitor"]["max-autoresolves-per-ticket"]
INTERMAPPER_OUTAGE_MONITOR__MAX_CONCURRENT_EMAIL_BATCHES = parameters["common"]["intermapper-outage-monitor"]["max-concurrent-email-batches"]
INTERMAPPER_OUTAGE_MONITOR__WHITELISTED_PRODUCT_CATEGORIES_FOR_AUTORESOLVE = json.dumps(json.loads(parameters["common"]["intermapper-outage-monitor"]["whitelisted-product-categories-for-autoresolve"]))
INTERMAPPER_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME = parameters["common"]["intermapper-outage-monitor"]["grace-period-to-autoresolve-after-last-documented-outage-day-time"]
INTERMAPPER_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME = parameters["common"]["intermapper-outage-monitor"]["grace-period-to-autoresolve-after-last-documented-outage-night-time"]
INTERMAPPER_OUTAGE_MONITOR__DRI_PARAMETERS_FOR_PIAB_NOTES = json.dumps(json.loads(parameters["common"]["intermapper-outage-monitor"]["dri-parameters-for-piab-notes"]))
INTERMAPPER_OUTAGE_MONITOR__EVENTS_LOOKUP_DAYS = parameters["common"]["intermapper-outage-monitor"]["events-lookup-days"]
INTERMAPPER_OUTAGE_MONITOR__BATTERY_ALERT_PROBE_TYPES = parameters["common"]["intermapper-outage-monitor"]["battery-alert-probe-types"]
INTERMAPPER_OUTAGE_MONITOR__BATTERY_ALERT_PROBE_CONDITIONS = parameters["common"]["intermapper-outage-monitor"]["battery-alert-probe-conditions"]
INTERMAPPER_OUTAGE_MONITOR__FORWARD_TO_HNOC_JOB_INTERVAL = parameters["common"]["intermapper-outage-monitor"]["forward-to-hnoc-job-interval"]
INTERMAPPER_OUTAGE_MONITOR__FORWARD_TO_IPA_JOB_INTERVAL = parameters["common"]["intermapper-outage-monitor"]["forward-to-ipa-job-interval"]

# Last Contact Report variables
LAST_CONTACT_REPORT__MONITORED_VELOCLOUD_HOSTS = parameters["dev"]["last-contact-report"]["monitored-velocloud-hosts"]
LAST_CONTACT_REPORT__RECIPIENT = parameters["dev"]["last-contact-report"]["report-recipient"]

# Email Bridge variables
EMAIL_BRIDGE__EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_USERNAME = parameters["common"]["email-bridge"]["email-account-for-message-delivery-username"]
EMAIL_BRIDGE__EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_PASSWORD = parameters["common"]["email-bridge"]["email-account-for-message-delivery-password"]
EMAIL_BRIDGE__MONITORABLE_EMAIL_ACCOUNTS = parameters["dev"]["email-bridge"]["monitorable-email-accounts"]

# Notifications bridge variables
NOTIFICATIONS_BRIDGE__SLACK_WEBHOOK = parameters["dev"]["notifications-bridge"]["slack-webhook-url"]

# RTA KRE Bridge variables
REPAIR_TICKETS_KRE_BRIDGE__KRE_BASE_URL = parameters["dev"]["repair-tickets-kre-bridge"]["kre-base-url"]

# RTA Monitor variables
REPAIR_TICKETS_MONITOR__RTA_MONITOR_JOB_INTERVAL = parameters["common"]["repair-tickets-monitor"]["rta-monitor-job-interval"]
REPAIR_TICKETS_MONITOR__NEW_CREATED_TICKETS_FEEDBACK_JOB_INTERVAL = parameters["common"]["repair-tickets-monitor"]["new-created-tickets-feedback-job-interval"]
REPAIR_TICKETS_MONITOR__NEW_CLOSED_TICKETS_FEEDBACK_JOB_INTERVAL = parameters["common"]["repair-tickets-monitor"]["new-closed-tickets-feedback-job-interval"]
REPAIR_TICKETS_MONITOR__OLD_PARENT_EMAILS_REPROCESSING_JOB_INTERVAL = parameters["common"]["repair-tickets-monitor"]["old-parent-emails-reprocessing-job-interval"]
REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_EMAILS_FOR_MONITORING = parameters["common"]["repair-tickets-monitor"]["max-concurrent-emails-for-monitoring"]
REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_CREATED_TICKETS_FOR_FEEDBACK = parameters["common"]["repair-tickets-monitor"]["max-concurrent-created-tickets-for-feedback"]
REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_CLOSED_TICKETS_FOR_FEEDBACK = parameters["common"]["repair-tickets-monitor"]["max-concurrent-closed-tickets-for-feedback"]
REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_OLD_PARENT_EMAILS_REPROCESSING = parameters["common"]["repair-tickets-monitor"]["max-concurrent-old-parent-emails-reprocessing"]
REPAIR_TICKETS_MONITOR__TAG_IDS_MAPPING = parameters["common"]["repair-tickets-monitor"]["tag-ids-mapping"]
REPAIR_TICKETS_MONITOR__AUTO_REPLY_ENABLED = parameters["dev"]["repair-tickets-monitor"]["auto-reply-enabled"]
REPAIR_TICKETS_MONITOR__AUTO_REPLY_WHITELIST = parameters["dev"]["repair-tickets-monitor"]["auto-reply-whitelist"]
REPAIR_TICKETS_MONITOR__OLD_PARENT_EMAIL_TTL_SECONDS = parameters["dev"]["repair-tickets-monitor"]["old-parent-email-ttl-seconds"]

# Service Affecting Monitor - Shared variables
SERVICE_AFFECTING__MONITORED_PRODUCT_CATEGORY = parameters["common"]["service-affecting"]["monitored-product-category"]

# Service Affecting Monitor - Monitoring variables
SERVICE_AFFECTING__MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["monitoring-job-interval"]
SERVICE_AFFECTING__MONITOR__MONITORED_VELOCLOUD_HOSTS = json.loads(parameters["dev"]["service-affecting"]["monitor"]["monitored-velocloud-hosts"])
SERVICE_AFFECTING__MONITOR__DEFAULT_CONTACT_INFO_PER_CUSTOMER = json.dumps(json.loads(parameters["common"]["service-affecting"]["monitor"]["default-contact-info-per-customer"]))
SERVICE_AFFECTING__MONITOR__CUSTOMERS_TO_ALWAYS_USE_DEFAULT_CONTACT_INFO = json.dumps(json.loads(parameters["common"]["service-affecting"]["monitor"]["customers-to-always-use-default-contact-info"]))
SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_THRESHOLD = parameters["common"]["service-affecting"]["monitor"]["latency-monitoring-threshold"]
SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_THRESHOLD = parameters["common"]["service-affecting"]["monitor"]["packet-loss-monitoring-threshold"]
SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_THRESHOLD = parameters["common"]["service-affecting"]["monitor"]["jitter-monitoring-threshold"]
SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD = parameters["common"]["service-affecting"]["monitor"]["bandwidth-over-utilization-monitoring-threshold"]
SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD = parameters["common"]["service-affecting"]["monitor"]["circuit-instability-monitoring-threshold"]
SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD = parameters["common"]["service-affecting"]["monitor"]["circuit-instability-autoresolve-threshold"]
SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["latency-monitoring-lookup-interval"]
SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["packet-loss-monitoring-lookup-interval"]
SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["jitter-monitoring-lookup-interval"]
SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["bandwidth-over-utilization-monitoring-lookup-interval"]
SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["circuit-instability-monitoring-lookup-interval"]
SERVICE_AFFECTING__MONITOR__AUTORESOLVE_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["monitor"]["autoresolve-lookup-interval"]
SERVICE_AFFECTING__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_DAY_TIME = parameters["common"]["service-affecting"]["monitor"]["grace-period-to-autoresolve-after-last-documented-trouble-day-time"]
SERVICE_AFFECTING__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_NIGHT_TIME = parameters["common"]["service-affecting"]["monitor"]["grace-period-to-autoresolve-after-last-documented-trouble-night-time"]
SERVICE_AFFECTING__MONITOR__MAX_AUTORESOLVES_PER_TICKET = parameters["common"]["service-affecting"]["monitor"]["max-autoresolves-per-ticket"]
SERVICE_AFFECTING__MONITOR__CUSTOMERS_WITH_BANDWIDTH_OVER_UTILIZATION_MONITORING = json.dumps(json.loads(parameters["common"]["service-affecting"]["monitor"]["customers-with-bandwidth-over-utilization-monitoring"]))
SERVICE_AFFECTING__MONITOR__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER = parameters["common"]["service-affecting"]["monitor"]["wait-time-before-sending-new-milestone-reminder"]

# Service Affecting Monitor - Reoccurring Trouble Report variables
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__EXECUTION_CRON_EXPRESSION = parameters["common"]["service-affecting"]["reoccurring-trouble-report"]["execution-cron-expression"]
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES = json.dumps(json.loads(parameters["common"]["service-affecting"]["reoccurring-trouble-report"]["reported-troubles"]))
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["reoccurring-trouble-report"]["tickets-lookup-interval"]
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD = parameters["common"]["service-affecting"]["reoccurring-trouble-report"]["reoccurring-trouble-tickets-threshold"]
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__DEFAULT_CONTACTS = json.dumps(json.loads(parameters["common"]["service-affecting"]["reoccurring-trouble-report"]["default-contacts"]))
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_HOST_AND_CUSTOMER = json.dumps(json.loads(parameters["common"]["service-affecting"]["reoccurring-trouble-report"]["recipients-per-host-and-customer"]))
SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__EXEC_ON_START = False

# Service Affecting Monitor - Daily Bandwidth Report variables
SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION = parameters["common"]["service-affecting"]["daily-bandwidth-report"]["execution-cron-expression"]
SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL = parameters["common"]["service-affecting"]["daily-bandwidth-report"]["lookup-interval"]
SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS_PER_HOST = json.dumps(json.loads(parameters["common"]["service-affecting"]["daily-bandwidth-report"]["enabled-customers-per-host"]))
SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__RECIPIENTS = json.dumps(json.loads(parameters["common"]["service-affecting"]["daily-bandwidth-report"]["recipients"]))
SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__EXEC_ON_START = False

# Service Outage Monitor - Shared variables
SERVICE_OUTAGE__MONITORED_PRODUCT_CATEGORY = parameters["common"]["service-outage"]["monitored-product-category"]

# Service Outage Monitor - Monitoring variables
SERVICE_OUTAGE__MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["service-outage"]["monitor"]["monitoring-job-interval"]
SERVICE_OUTAGE__MONITOR__MONITORED_VELOCLOUD_HOSTS = json.loads(parameters["dev"]["service-outage"]["monitor"]["monitored-velocloud-hosts"])
SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_LINK_DOWN_OUTAGE = parameters["common"]["service-outage"]["monitor"]["quarantine-for-edges-in-link-down-outage"]
SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HARD_DOWN_OUTAGE = parameters["common"]["service-outage"]["monitor"]["quarantine-for-edges-in-hard-down-outage"]
SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_LINK_DOWN_OUTAGE = parameters["common"]["service-outage"]["monitor"]["quarantine-for-edges-in-ha-link-down-outage"]
SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_SOFT_DOWN_OUTAGE = parameters["common"]["service-outage"]["monitor"]["quarantine-for-edges-in-ha-soft-down-outage"]
SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_HARD_DOWN_OUTAGE = parameters["common"]["service-outage"]["monitor"]["quarantine-for-edges-in-ha-hard-down-outage"]
SERVICE_OUTAGE__MONITOR__BLACKLISTED_EDGES = json.dumps(json.loads(parameters["dev"]["service-outage"]["monitor"]["blacklisted-edges"]))
SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME = parameters["common"]["service-outage"]["monitor"]["grace-period-to-autoresolve-after-last-documented-outage-day-time"]
SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME = parameters["common"]["service-outage"]["monitor"]["grace-period-to-autoresolve-after-last-documented-outage-night-time"]
SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_BEFORE_ATTEMPTING_NEW_DIGI_REBOOTS = parameters["common"]["service-outage"]["monitor"]["grace-period-before-attempting-new-digi-reboots"]
SERVICE_OUTAGE__MONITOR__SEVERITY_FOR_EDGE_DOWN_OUTAGES = parameters["common"]["service-outage"]["monitor"]["severity-for-edge-down-outages"]
SERVICE_OUTAGE__MONITOR__SEVERITY_FOR_LINK_DOWN_OUTAGES = parameters["common"]["service-outage"]["monitor"]["severity-for-link-down-outages"]
SERVICE_OUTAGE__MONITOR__MAX_AUTORESOLVES_PER_TICKET = parameters["common"]["service-outage"]["monitor"]["max-autoresolves-per-ticket"]
SERVICE_OUTAGE__MONITOR__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER = parameters["common"]["service-outage"]["monitor"]["wait-time-before-sending-new-milestone-reminder"]
SERVICE_OUTAGE__MONITOR__BUSINESS_GRADE_LINK_LABELS = json.dumps(json.loads(parameters["common"]["service-outage"]["monitor"]["business-grade-link-labels"]))

# Service Outage Monitor - Triage variables
SERVICE_OUTAGE__TRIAGE__MONITORING_JOB_INTERVAL = parameters["common"]["service-outage"]["triage"]["monitoring-job-interval"]
SERVICE_OUTAGE__TRIAGE__LAST_NOTE_INTERVAL = parameters["common"]["service-outage"]["triage"]["last-note-interval"]
SERVICE_OUTAGE__TRIAGE__MONITORED_VELOCLOUD_HOSTS = json.dumps(json.loads(parameters["dev"]["service-outage"]["triage"]["monitored-velocloud-hosts"]))
SERVICE_OUTAGE__TRIAGE__MAX_EVENTS_PER_EVENT_NOTE = parameters["common"]["service-outage"]["triage"]["max-events-per-event-note"]

# ServiceNow Bridge variables
SERVICENOW__BASE_URL = parameters["dev"]["servicenow-bridge"]["base-url"]
SERVICENOW__CLIENT_ID = parameters["common"]["servicenow-bridge"]["client-id"]
SERVICENOW__CLIENT_SECRET = parameters["common"]["servicenow-bridge"]["client-secret"]
SERVICENOW__USERNAME = parameters["common"]["servicenow-bridge"]["username"]
SERVICENOW__PASSWORD = parameters["common"]["servicenow-bridge"]["password"]

# Task Dispatcher variables
TASK_DISPATCHER__DISPATCHING_JOB_INTERVAL = parameters["common"]["task-dispatcher"]["dispatching-job-interval"]

# TNBA Feedback variables
TNBA_FEEDBACK__FEEDBACK_JOB_INTERVAL = parameters["common"]["tnba-feedback"]["feedback-job-interval"]
TNBA_FEEDBACK__MONITORED_VELOCLOUD_HOSTS = json.dumps(json.loads(parameters["dev"]["tnba-feedback"]["monitored-velocloud-hosts"]))
TNBA_FEEDBACK__MONITORED_PRODUCT_CATEGORY = parameters["common"]["tnba-feedback"]["monitored-product-category"]
TNBA_FEEDBACK__GRACE_PERIOD_BEFORE_RESENDING_TICKETS = parameters["common"]["tnba-feedback"]["grace-period-before-resending-tickets"]

# TNBA Monitor variables
TNBA_MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["tnba-monitor"]["monitoring-job-interval"]
TNBA_MONITOR__MONITORED_VELOCLOUD_HOSTS = json.loads(parameters["dev"]["tnba-monitor"]["monitored-velocloud-hosts"])
TNBA_MONITOR__MONITORED_PRODUCT_CATEGORY = parameters["common"]["tnba-monitor"]["monitored-product-category"]
TNBA_MONITOR__BLACKLISTED_EDGES = parameters["dev"]["tnba-monitor"]["blacklisted-edges"]
TNBA_MONITOR__GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES = parameters["common"]["tnba-monitor"]["grace-period-before-appending-new-tnba-notes"]
TNBA_MONITOR__GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE = parameters["common"]["tnba-monitor"]["grace-period-before-monitoring-tickets-based-on-last-documented-outage"]
TNBA_MONITOR__MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS = parameters["common"]["tnba-monitor"]["min-required-confidence-for-request-and-repair-completed-predictions"]

# Forticloud Poller variables
FORTICLOUD_POLLER__MONITORING_JOB_INTERVAL = parameters["common"]["forticloud-poller"]["monitoring-job-interval"]

# Gateway Monitor
GATEWAY_MONITOR__MONITORED_VELOCLOUD_HOSTS = json.dumps(json.loads(parameters["dev"]["gateway-monitor"]["monitored-velocloud-hosts"]))
GATEWAY_MONITOR__MONITORING_JOB_INTERVAL = parameters["common"]["gateway-monitor"]["monitoring-job-interval"]
GATEWAY_MONITOR__GATEWAY_METRICS_LOOKUP_INTERVAL = parameters["common"]["gateway-monitor"]["gateway-metrics-lookup-interval"]
GATEWAY_MONITOR__BLACKLISTED_GATEWAYS = parameters["common"]["gateway-monitor"]["blacklisted-gateways"]
GATEWAY_MONITOR__OFFLINE_TROUBLE_ENABLED = parameters["common"]["gateway-monitor"]["offline-trouble-enabled"]
GATEWAY_MONITOR__TUNNEL_COUNT_TROUBLE_ENABLED = parameters["common"]["gateway-monitor"]["tunnel-count-trouble-enabled"]
GATEWAY_MONITOR__TUNNEL_COUNT_THRESHOLD = parameters["common"]["gateway-monitor"]["tunnel-count-threshold"]

# Lumin Billing Report variables
LUMIN_URI = parameters["common"]["lumin-billing-report"]["lumin-billing-api-base-url"]
LUMIN_TOKEN = parameters["common"]["lumin-billing-report"]["access-token"]
CUSTOMER_NAME = parameters["common"]["lumin-billing-report"]["customer-name"]
BILLING_RECIPIENT = parameters["common"]["lumin-billing-report"]["recipient"]
EMAIL_ACC_PWD = parameters["common"]["lumin-billing-report"]["email-account-for-message-delivery-password"]

# NATS variables
NATS_CLUSTER_NAME = ""
NATS_SERVER1 = "nats://nats-server:4222"
NATSROUTECLUSTER = "nats://nats-server:5222"
NATSCLUSTER1 = "nats://nats-server:5222"
NATSCLUSTER2 = "nats://nats-server-1:5223"
NATSCLUSTER3 = "nats://nats-server-2:5224"
NATS_PORT1 = 4222
NATS_PORT2 = 4223
NATS_PORT3 = 4224
NATS_CLUSTER_MODE1 = "s"
NATS_CLUSTER_MODE2 = "n"
NATS_CLUSTER_MODE3 = "n"

# Redis variables
REDIS_HOSTNAME = "redis"
REDIS_CUSTOMER_CACHE_HOSTNAME = "redis-customer-cache"
REDIS_TNBA_FEEDBACK_HOSTNAME = "redis-tnba-feedback"
REDIS_EMAIL_TAGGER_HOSTNAME = "redis-email-tagger"

# MongoDB variables
MONGODB_HOST = "mongo"
MONGODB_USERNAME = "root"
MONGODB_PASSWORD = "example"
MONGODB_DATABASE = "bruin"
MONGODB_PORT = 27017

# Links Metrics Collector variables
MONGODB_LINKS_HOST = "mongo-links-metrics"

# T7 Bridge variables
KRE_TNBA_BASE_URL = parameters["dev"]["t7-bridge"]["kre-base-url"]

# Email Tagger KRE Bridge variables
EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL = parameters["dev"]["email-tagger-kre-bridge"]["kre-base-url"]

# Email Tagger Monitor variables
EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL = parameters["common"]["email-tagger-monitor"]["new-emails-job-interval"]
EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL = parameters["common"]["email-tagger-monitor"]["new-tickets-job-interval"]
EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS = parameters["common"]["email-tagger-monitor"]["max-concurrent-emails"]
EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS = parameters["common"]["email-tagger-monitor"]["max-concurrent-tickets"]
EMAIL_TAGGER_MONITOR__API_REQUEST_KEY = parameters["dev"]["email-tagger-monitor"]["api-request-key"]
EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY = parameters["dev"]["email-tagger-monitor"]["api-request-signature-secret-key"]
EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX = parameters["common"]["email-tagger-monitor"]["api-endpoint-prefix"]
EMAIL_TAGGER_MONITOR__STORE_REPLIES_ENABLED = parameters["dev"]["email-tagger-monitor"]["store-replies-enabled"]

# Velocloud variables
VELOCLOUD_CREDENTIALS = parameters["dev"]["velocloud-bridge"]["velocloud-credentials"]

# Papertrail variables
PAPERTRAIL_ACTIVE = False
PAPERTRAIL_PORT = 1111
PAPERTRAIL_HOST = "logs.papertrailapp.com"

env_dict = {
    os.path.join("base-microservice", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
    ],
    os.path.join("services", "bruin-bridge", "src", "config", "env"): [
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"BRUIN_CLIENT_ID={BRUIN_CLIENT_ID}",
        f"BRUIN_CLIENT_SECRET={BRUIN_CLIENT_SECRET}",
        f"BRUIN_LOGIN_URL={BRUIN_LOGIN_URL}",
        f"BRUIN_BASE_URL={BRUIN_BASE_URL}",
        f"IPA_SYSTEM_USERNAME_IN_BRUIN={IPA_SYSTEM_USERNAME_IN_BRUIN}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "digi-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"DIGI_CLIENT_ID={DIGI_CLIENT_ID}",
        f"DIGI_CLIENT_SECRET={DIGI_CLIENT_SECRET}",
        f"DIGI_BASE_URL={DIGI_BASE_URL}",
        f"DIGI_TOKEN_TTL={DIGI_TOKEN_TTL}",
        f"TIMEZONE={TIMEZONE}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "digi-reboot-report", "src", "config", "env"): [
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"JOB_INTERVAL={DIGI_REBOOT_REPORT__JOB_INTERVAL}",
        f"LOGS_LOOKUP_INTERVAL={DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL}",
        f"RECIPIENT={DIGI_REBOOT_REPORT__RECIPIENT}",
        f"TIMEZONE={TIMEZONE}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "dri-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"USERNAME={DRI_BRIDGE__USERNAME}",
        f"PASSWORD={DRI_BRIDGE__PASSWORD}",
        f"BASE_URL={DRI_BRIDGE__BASE_URL}",
        f"DRI_DATA_REDIS_TTL={DRI_BRIDGE__DRI_DATA_REDIS_TTL}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "customer-cache", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"REDIS_CUSTOMER_CACHE_HOSTNAME={REDIS_CUSTOMER_CACHE_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"VELOCLOUD_HOSTS={CUSTOMER_CACHE__VELOCLOUD_HOSTS}",
        f"DUPLICATE_INVENTORIES_RECIPIENT={CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}",
        f"REFRESH_JOB_INTERVAL={CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}",
        f"REFRESH_CHECK_INTERVAL={CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL}",
        f"BLACKLISTED_EDGES={CUSTOMER_CACHE__BLACKLISTED_EDGES}",
        f"BLACKLISTED_CLIENTS_WITH_PENDING_STATUS={CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS}",
        f"WHITELISTED_MANAGEMENT_STATUSES={CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}",
    ],
    os.path.join("services", "email-tagger-kre-bridge", "src", "config", "env"): [
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"KRE_BASE_URL={EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "email-tagger-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"REDIS_EMAIL_TAGGER_HOSTNAME={REDIS_EMAIL_TAGGER_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"TIMEZONE={TIMEZONE}",
        f"API_REQUEST_KEY={EMAIL_TAGGER_MONITOR__API_REQUEST_KEY}",
        f"API_REQUEST_SIGNATURE_SECRET_KEY={EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY}",
        f"API_ENDPOINT_PREFIX={EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX}",
        f"NEW_EMAILS_JOB_INTERVAL={EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL}",
        f"NEW_TICKETS_JOB_INTERVAL={EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL}",
        f"MAX_CONCURRENT_EMAILS={EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS}",
        f"MAX_CONCURRENT_TICKETS={EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS}",
        f"STORE_REPLIES_ENABLED={EMAIL_TAGGER_MONITOR__STORE_REPLIES_ENABLED}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "forticloud-cache", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"TIMEZONE={TIMEZONE}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"FORTICLOUD_BASE_URL={FORTICLOUD_BASE_URL}",
        f"FORTICLOUD_USERNAME={FORTICLOUD_USERNAME}",
        f"FORTICLOUD_PASSWORD={FORTICLOUD_PASSWORD}",
        f"FORTICLOUD_ACCOUNT={FORTICLOUD_ACCOUNT}",
    ],
    os.path.join("services", "forticloud-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f'NATS_SERVER={NATS_SERVER1}',
        f'BRUIN_BASE_URL={BRUIN_BASE_URL}',
        f'BRUIN_LOGIN_URL={BRUIN_LOGIN_URL}',
        f'BRUIN_CLIENT_ID={BRUIN_CLIENT_ID}',
        f'BRUIN_CLIENT_SECRET={BRUIN_CLIENT_SECRET}',
        f'FORTICLOUD_BASE_URL={FORTICLOUD_BASE_URL}',
        f'FORTICLOUD_USERNAME={FORTICLOUD_USERNAME}',
        f'FORTICLOUD_PASSWORD={FORTICLOUD_PASSWORD}',
        f'FORTICLOUD_ACCOUNT={FORTICLOUD_ACCOUNT}',
    ],
    os.path.join("services", "forticloud-poller", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"TIMEZONE={TIMEZONE}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"MONITORING_JOB_INTERVAL={FORTICLOUD_POLLER__MONITORING_JOB_INTERVAL}",
    ],
    os.path.join("services", "fraud-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"MONITORING_JOB_INTERVAL={FRAUD_MONITOR__MONITORING_JOB_INTERVAL}",
        f"OBSERVED_INBOX_EMAIL_ADDRESS={FRAUD_MONITOR__OBSERVED_INBOX_EMAIL_ADDRESS}",
        f"OBSERVED_INBOX_SENDERS={FRAUD_MONITOR__OBSERVED_INBOX_SENDERS}",
        f"DEFAULT_CONTACT_FOR_NEW_TICKETS={FRAUD_MONITOR__DEFAULT_CONTACT_FOR_NEW_TICKETS}",
        f"DEFAULT_CLIENT_INFO_FOR_DID_WITHOUT_INVENTORY={FRAUD_MONITOR__DEFAULT_CLIENT_INFO_FOR_DID_WITHOUT_INVENTORY}",
        f"ALERTS_LOOKUP_DAYS={FRAUD_MONITOR__ALERTS_LOOKUP_DAYS}",
    ],
    os.path.join("services", "hawkeye-affecting-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"TIMEZONE={TIMEZONE}",
        f"MONITORING_JOB_INTERVAL={HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL}",
        f"PROBES_TESTS_RESULTS_LOOKUP_INTERVAL={HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL}",
        f"MONITORED_PRODUCT_CATEGORY={HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "hawkeye-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CLIENT_USERNAME={HAWKEYE_BRIDGE__CLIENT_USERNAME}",
        f"CLIENT_PASSWORD={HAWKEYE_BRIDGE__CLIENT_PASSWORD}",
        f"BASE_URL={HAWKEYE_BRIDGE__BASE_URL}",
    ],
    os.path.join("services", "hawkeye-customer-cache", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"REDIS_CUSTOMER_CACHE_HOSTNAME={REDIS_CUSTOMER_CACHE_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"DUPLICATE_INVENTORIES_RECIPIENT={HAWKEYE_CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}",
        f"REFRESH_JOB_INTERVAL={HAWKEYE_CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}",
        f"WHITELISTED_MANAGEMENT_STATUSES={HAWKEYE_CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}",
    ],
    os.path.join("services", "hawkeye-outage-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"IPA_SYSTEM_USERNAME_IN_BRUIN={IPA_SYSTEM_USERNAME_IN_BRUIN}",
        f"METRICS_RELEVANT_CLIENTS={METRICS_RELEVANT_CLIENTS}",
        f"MONITORING_JOB_INTERVAL={HAWKEYE_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL}",
        f"QUARANTINE_FOR_DEVICES_IN_OUTAGE={HAWKEYE_OUTAGE_MONITOR__QUARANTINE_FOR_DEVICES_IN_OUTAGE}",
        f"MONITORED_PRODUCT_CATEGORY={HAWKEYE_OUTAGE_MONITOR__MONITORED_PRODUCT_CATEGORY}",
        f"GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE={HAWKEYE_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE}",
    ],
    os.path.join("services", "intermapper-outage-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"MONITORING_JOB_INTERVAL={INTERMAPPER_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL}",
        f"OBSERVED_INBOX_EMAIL_ADDRESS={INTERMAPPER_OUTAGE_MONITOR__OBSERVED_INBOX_EMAIL_ADDRESS}",
        f"OBSERVED_INBOX_SENDERS={INTERMAPPER_OUTAGE_MONITOR__OBSERVED_INBOX_SENDERS}",
        f"MONITORED_DOWN_EVENTS={INTERMAPPER_OUTAGE_MONITOR__MONITORED_DOWN_EVENTS}",
        f"MONITORED_UP_EVENTS={INTERMAPPER_OUTAGE_MONITOR__MONITORED_UP_EVENTS}",
        f"MAX_AUTORESOLVES_PER_TICKET={INTERMAPPER_OUTAGE_MONITOR__MAX_AUTORESOLVES_PER_TICKET}",
        f"MAX_CONCURRENT_EMAIL_BATCHES={INTERMAPPER_OUTAGE_MONITOR__MAX_CONCURRENT_EMAIL_BATCHES}",
        f"WHITELISTED_PRODUCT_CATEGORIES_FOR_AUTORESOLVE={INTERMAPPER_OUTAGE_MONITOR__WHITELISTED_PRODUCT_CATEGORIES_FOR_AUTORESOLVE}",
        f"AUTORESOLVE_DAY_START_HOUR={AUTORESOLVE_DAY_START_HOUR}",
        f"AUTORESOLVE_DAY_END_HOUR={AUTORESOLVE_DAY_END_HOUR}",
        f"GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME={INTERMAPPER_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME}",
        f"GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME={INTERMAPPER_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME}",
        f"DRI_PARAMETERS_FOR_PIAB_NOTES={INTERMAPPER_OUTAGE_MONITOR__DRI_PARAMETERS_FOR_PIAB_NOTES}",
        f"EVENTS_LOOKUP_DAYS={INTERMAPPER_OUTAGE_MONITOR__EVENTS_LOOKUP_DAYS}",
        f"BATTERY_ALERT_PROBE_TYPES={INTERMAPPER_OUTAGE_MONITOR__BATTERY_ALERT_PROBE_TYPES}",
        f"BATTERY_ALERT_PROBE_CONDITIONS={INTERMAPPER_OUTAGE_MONITOR__BATTERY_ALERT_PROBE_CONDITIONS}",
        f"FORWARD_TO_HNOC_JOB_INTERVAL={INTERMAPPER_OUTAGE_MONITOR__FORWARD_TO_HNOC_JOB_INTERVAL}",
        f"FORWARD_TO_IPA_JOB_INTERVAL={INTERMAPPER_OUTAGE_MONITOR__FORWARD_TO_IPA_JOB_INTERVAL}",
    ],
    os.path.join("services", "last-contact-report", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"TIMEZONE={TIMEZONE}",
        f"MONITORED_VELOCLOUD_HOSTS={LAST_CONTACT_REPORT__MONITORED_VELOCLOUD_HOSTS}",
        f"RECIPIENT={LAST_CONTACT_REPORT__RECIPIENT}",
    ],
    os.path.join("metrics-dashboard", "grafana", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
    ],
    os.path.join("services", "email-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_USERNAME={EMAIL_BRIDGE__EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_USERNAME}",
        f"EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_PASSWORD={EMAIL_BRIDGE__EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_PASSWORD}",
        f"MONITORABLE_EMAIL_ACCOUNTS={EMAIL_BRIDGE__MONITORABLE_EMAIL_ACCOUNTS}",
    ],
    os.path.join("services", "notifications-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"SLACK_WEBHOOK={NOTIFICATIONS_BRIDGE__SLACK_WEBHOOK}"
    ],
    os.path.join("services", "repair-tickets-kre-bridge", "src", "config", "env"): [
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"KRE_BASE_URL={REPAIR_TICKETS_KRE_BRIDGE__KRE_BASE_URL}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "repair-tickets-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"REDIS_EMAIL_TAGGER_HOSTNAME={REDIS_EMAIL_TAGGER_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"IPA_SYSTEM_USERNAME_IN_BRUIN={IPA_SYSTEM_USERNAME_IN_BRUIN}",
        f"RTA_MONITOR_JOB_INTERVAL={REPAIR_TICKETS_MONITOR__RTA_MONITOR_JOB_INTERVAL}",
        f"NEW_CREATED_TICKETS_FEEDBACK_JOB_INTERVAL={REPAIR_TICKETS_MONITOR__NEW_CREATED_TICKETS_FEEDBACK_JOB_INTERVAL}",
        f"NEW_CLOSED_TICKETS_FEEDBACK_JOB_INTERVAL={REPAIR_TICKETS_MONITOR__NEW_CLOSED_TICKETS_FEEDBACK_JOB_INTERVAL}",
        f"OLD_PARENT_EMAILS_REPROCESSING_JOB_INTERVAL={REPAIR_TICKETS_MONITOR__OLD_PARENT_EMAILS_REPROCESSING_JOB_INTERVAL}",
        f"MAX_CONCURRENT_EMAILS_FOR_MONITORING={REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_EMAILS_FOR_MONITORING}",
        f"MAX_CONCURRENT_CREATED_TICKETS_FOR_FEEDBACK={REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_CREATED_TICKETS_FOR_FEEDBACK}",
        f"MAX_CONCURRENT_CLOSED_TICKETS_FOR_FEEDBACK={REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_CLOSED_TICKETS_FOR_FEEDBACK}",
        f"MAX_CONCURRENT_OLD_PARENT_EMAILS_REPROCESSING={REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_OLD_PARENT_EMAILS_REPROCESSING}",
        f"TAG_IDS_MAPPING={REPAIR_TICKETS_MONITOR__TAG_IDS_MAPPING}",
        f"AUTO_REPLY_ENABLED={REPAIR_TICKETS_MONITOR__AUTO_REPLY_ENABLED}",
        f"AUTO_REPLY_WHITELIST={REPAIR_TICKETS_MONITOR__AUTO_REPLY_WHITELIST}",
        f"OLD_PARENT_EMAIL_TTL_SECONDS={REPAIR_TICKETS_MONITOR__OLD_PARENT_EMAIL_TTL_SECONDS}",
    ],
    os.path.join("services", "lumin-billing-report", "src", "config", "env"): [
        f"LUMIN_URI={LUMIN_URI}",
        f"LUMIN_TOKEN={LUMIN_TOKEN}",
        f"CUSTOMER_NAME={CUSTOMER_NAME}",
        f"BILLING_RECIPIENT={BILLING_RECIPIENT}",
        f"EMAIL_ACC_PWD={EMAIL_ACC_PWD}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("nats-server", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CLUSTER_MODE={NATS_CLUSTER_MODE1}",
        f"NATSCLUSTER={NATSCLUSTER1}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"PORT={NATS_PORT1}",
    ],
    os.path.join("nats-server", "nats-server-1-env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CLUSTER_MODE={NATS_CLUSTER_MODE2}",
        f"NATSCLUSTER={NATSCLUSTER2}",
        f"NATSROUTECLUSTER={NATSROUTECLUSTER}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"PORT={NATS_PORT2}",
    ],
    os.path.join("nats-server", "nats-server-2-env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CLUSTER_MODE={NATS_CLUSTER_MODE3}",
        f"NATSCLUSTER={NATSCLUSTER3}",
        f"NATSROUTECLUSTER={NATSROUTECLUSTER}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"PORT={NATS_PORT3}",
    ],
    os.path.join("services", "service-outage-monitor", "src", "config", "env-triage"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"ENABLE_TRIAGE_MONITORING=1",
        f"TIMEZONE={TIMEZONE}",
        f"MONITORED_PRODUCT_CATEGORY={SERVICE_OUTAGE__MONITORED_PRODUCT_CATEGORY}",
        f"TRIAGE__MONITORING_JOB_INTERVAL={SERVICE_OUTAGE__TRIAGE__MONITORING_JOB_INTERVAL}",
        f"TRIAGE__LAST_NOTE_INTERVAL={SERVICE_OUTAGE__TRIAGE__LAST_NOTE_INTERVAL}",
        f"TRIAGE__MONITORED_VELOCLOUD_HOSTS={SERVICE_OUTAGE__TRIAGE__MONITORED_VELOCLOUD_HOSTS}",
        f"TRIAGE__MAX_EVENTS_PER_EVENT_NOTE={SERVICE_OUTAGE__TRIAGE__MAX_EVENTS_PER_EVENT_NOTE}",
    ],
    os.path.join("services", "t7-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"KRE_BASE_URL={KRE_TNBA_BASE_URL}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "tnba-feedback", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"REDIS_TNBA_FEEDBACK_HOSTNAME={REDIS_TNBA_FEEDBACK_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"FEEDBACK_JOB_INTERVAL={TNBA_FEEDBACK__FEEDBACK_JOB_INTERVAL}",
        f"MONITORED_VELOCLOUD_HOSTS={TNBA_FEEDBACK__MONITORED_VELOCLOUD_HOSTS}",
        f"MONITORED_PRODUCT_CATEGORY={TNBA_FEEDBACK__MONITORED_PRODUCT_CATEGORY}",
        f"GRACE_PERIOD_BEFORE_RESENDING_TICKETS={TNBA_FEEDBACK__GRACE_PERIOD_BEFORE_RESENDING_TICKETS}",
    ],
    os.path.join("services", "velocloud-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"VELOCLOUD_CREDENTIALS={VELOCLOUD_CREDENTIALS}",
        f"TIMEZONE={TIMEZONE}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "gateway-monitor", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"TIMEZONE={TIMEZONE}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"MONITORED_VELOCLOUD_HOSTS={GATEWAY_MONITOR__MONITORED_VELOCLOUD_HOSTS}",
        f"MONITORING_JOB_INTERVAL={GATEWAY_MONITOR__MONITORING_JOB_INTERVAL}",
        f"GATEWAY_METRICS_LOOKUP_INTERVAL={GATEWAY_MONITOR__GATEWAY_METRICS_LOOKUP_INTERVAL}",
        f"BLACKLISTED_GATEWAYS={GATEWAY_MONITOR__BLACKLISTED_GATEWAYS}",
        f"OFFLINE_TROUBLE_ENABLED={GATEWAY_MONITOR__OFFLINE_TROUBLE_ENABLED}",
        f"TUNNEL_COUNT_TROUBLE_ENABLED={GATEWAY_MONITOR__TUNNEL_COUNT_TROUBLE_ENABLED}",
        f"TUNNEL_COUNT_THRESHOLD={GATEWAY_MONITOR__TUNNEL_COUNT_THRESHOLD}",
    ],
    os.path.join("services", "links-metrics-collector", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"MONGO_URL={MONGODB_LINKS_HOST}",
        f"MONGO_USERNAME={MONGODB_USERNAME}",
        f"MONGO_PASS={MONGODB_PASSWORD}",
        f"MONGO_PORT={MONGODB_PORT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "links-metrics-api", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"MONGO_URL={MONGODB_LINKS_HOST}",
        f"MONGO_USERNAME={MONGODB_USERNAME}",
        f"MONGO_PASS={MONGODB_PASSWORD}",
        f"MONGO_PORT={MONGODB_PORT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
    ],
    os.path.join("services", "servicenow-bridge", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"BASE_URL={SERVICENOW__BASE_URL}",
        f"CLIENT_ID={SERVICENOW__CLIENT_ID}",
        f"CLIENT_SECRET={SERVICENOW__CLIENT_SECRET}",
        f"USERNAME={SERVICENOW__USERNAME}",
        f"PASSWORD={SERVICENOW__PASSWORD}",
    ],
    os.path.join("services", "task-dispatcher", "src", "config", "env"): [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"DISPATCHING_JOB_INTERVAL={TASK_DISPATCHER__DISPATCHING_JOB_INTERVAL}",
    ],
}

for host in SERVICE_OUTAGE__MONITOR__MONITORED_VELOCLOUD_HOSTS:
    filename = f'env-som-{host.replace(".", "-")}'
    env_dict[os.path.join("services", "service-outage-monitor", "src", "config", filename)] = [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"ENABLE_TRIAGE_MONITORING=0",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"METRICS_RELEVANT_CLIENTS={METRICS_RELEVANT_CLIENTS}",
        f"MONITORED_PRODUCT_CATEGORY={SERVICE_OUTAGE__MONITORED_PRODUCT_CATEGORY}",
        f"IPA_SYSTEM_USERNAME_IN_BRUIN={IPA_SYSTEM_USERNAME_IN_BRUIN}",
        f"LINK_LABELS_BLACKLISTED_FROM_ASR_FORWARDS={LINK_LABELS_BLACKLISTED_FROM_ASR_FORWARDS}",
        f"LINK_LABELS_BLACKLISTED_FROM_HNOC_FORWARDS={LINK_LABELS_BLACKLISTED_FROM_HNOC_FORWARDS}",
        f"DIGI_HEADERS={DIGI_HEADERS}",
        f"MONITORING__MONITORING_JOB_INTERVAL={SERVICE_OUTAGE__MONITOR__MONITORING_JOB_INTERVAL}",
        f"MONITORING__QUARANTINE_FOR_EDGES_IN_LINK_DOWN_OUTAGE={SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_LINK_DOWN_OUTAGE}",
        f"MONITORING__QUARANTINE_FOR_EDGES_IN_HARD_DOWN_OUTAGE={SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HARD_DOWN_OUTAGE}",
        f"MONITORING__QUARANTINE_FOR_EDGES_IN_HA_LINK_DOWN_OUTAGE={SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_LINK_DOWN_OUTAGE}",
        f"MONITORING__QUARANTINE_FOR_EDGES_IN_HA_SOFT_DOWN_OUTAGE={SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_SOFT_DOWN_OUTAGE}",
        f"MONITORING__QUARANTINE_FOR_EDGES_IN_HA_HARD_DOWN_OUTAGE={SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_HARD_DOWN_OUTAGE}",
        f"MONITORING__AUTORESOLVE_DAY_START_HOUR={AUTORESOLVE_DAY_START_HOUR}",
        f"MONITORING__AUTORESOLVE_DAY_END_HOUR={AUTORESOLVE_DAY_END_HOUR}",
        f"MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME={SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_DAY_TIME}",
        f"MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME={SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE_NIGHT_TIME}",
        f"MONITORING__GRACE_PERIOD_BEFORE_ATTEMPTING_NEW_DIGI_REBOOTS={SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_BEFORE_ATTEMPTING_NEW_DIGI_REBOOTS}",
        f"MONITORING__SEVERITY_FOR_EDGE_DOWN_OUTAGES={SERVICE_OUTAGE__MONITOR__SEVERITY_FOR_EDGE_DOWN_OUTAGES}",
        f"MONITORING__SEVERITY_FOR_LINK_DOWN_OUTAGES={SERVICE_OUTAGE__MONITOR__SEVERITY_FOR_LINK_DOWN_OUTAGES}",
        f"MONITORING__VELOCLOUD_HOST={host}",
        f"MONITORING__BLACKLISTED_EDGES={SERVICE_OUTAGE__MONITOR__BLACKLISTED_EDGES}",
        f"MONITORING__MAX_AUTORESOLVES_PER_TICKET={SERVICE_OUTAGE__MONITOR__MAX_AUTORESOLVES_PER_TICKET}",
        f"MONITORING__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER={SERVICE_OUTAGE__MONITOR__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER}",
        f"MONITORING__BUSINESS_GRADE_LINK_LABELS={SERVICE_OUTAGE__MONITOR__BUSINESS_GRADE_LINK_LABELS}",
    ]

for host in SERVICE_AFFECTING__MONITOR__MONITORED_VELOCLOUD_HOSTS:
    filename = f'env-sam-{host.replace(".", "-")}'
    env_dict[os.path.join("services", "service-affecting-monitor", "src", "config", filename)] = [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE=False",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"EXEC_MONITOR_REPORTS_ON_START={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__EXEC_ON_START}",
        f"EXEC_BANDWIDTH_REPORTS_ON_START={SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__EXEC_ON_START}",
        f"TIMEZONE={TIMEZONE}",
        f"METRICS_RELEVANT_CLIENTS={METRICS_RELEVANT_CLIENTS}",
        f"MONITORED_PRODUCT_CATEGORY={SERVICE_AFFECTING__MONITORED_PRODUCT_CATEGORY}",
        f"MONITORED_VELOCLOUD_HOST={host}",
        f"IPA_SYSTEM_USERNAME_IN_BRUIN={IPA_SYSTEM_USERNAME_IN_BRUIN}",
        f"LINK_LABELS_BLACKLISTED_FROM_ASR_FORWARDS={LINK_LABELS_BLACKLISTED_FROM_ASR_FORWARDS}",
        f"LINK_LABELS_BLACKLISTED_FROM_HNOC_FORWARDS={LINK_LABELS_BLACKLISTED_FROM_HNOC_FORWARDS}",
        f"MONITORING__MONITORING_JOB_INTERVAL={SERVICE_AFFECTING__MONITOR__MONITORING_JOB_INTERVAL}",
        f"MONITORING__DEFAULT_CONTACT_INFO_PER_CUSTOMER={SERVICE_AFFECTING__MONITOR__DEFAULT_CONTACT_INFO_PER_CUSTOMER}",
        f"MONITORING__CUSTOMERS_TO_ALWAYS_USE_DEFAULT_CONTACT_INFO={SERVICE_AFFECTING__MONITOR__CUSTOMERS_TO_ALWAYS_USE_DEFAULT_CONTACT_INFO}",
        f"MONITORING__LATENCY_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_THRESHOLD}",
        f"MONITORING__PACKET_LOSS_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_THRESHOLD}",
        f"MONITORING__JITTER_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_THRESHOLD}",
        f"MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD}",
        f"MONITORING__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD}",
        f"MONITORING__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD={SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD}",
        f"MONITORING__LATENCY_MONITORING_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_LOOKUP_INTERVAL}",
        f"MONITORING__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL}",
        f"MONITORING__JITTER_MONITORING_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_LOOKUP_INTERVAL}",
        f"MONITORING__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL}",
        f"MONITORING__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL}",
        f"MONITORING__AUTORESOLVE_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__AUTORESOLVE_LOOKUP_INTERVAL}",
        f"MONITORING__AUTORESOLVE_DAY_START_HOUR={AUTORESOLVE_DAY_START_HOUR}",
        f"MONITORING__AUTORESOLVE_DAY_END_HOUR={AUTORESOLVE_DAY_END_HOUR}",
        f"MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_DAY_TIME={SERVICE_AFFECTING__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_DAY_TIME}",
        f"MONITORING__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_NIGHT_TIME={SERVICE_AFFECTING__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE_NIGHT_TIME}",
        f"MONITORING__MAX_AUTORESOLVES_PER_TICKET={SERVICE_AFFECTING__MONITOR__MAX_AUTORESOLVES_PER_TICKET}",
        f"MONITORING__CUSTOMERS_WITH_BANDWIDTH_MONITORING_ENABLED={SERVICE_AFFECTING__MONITOR__CUSTOMERS_WITH_BANDWIDTH_OVER_UTILIZATION_MONITORING}",
        f"MONITORING__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER={SERVICE_AFFECTING__MONITOR__WAIT_TIME_BEFORE_SENDING_NEW_MILESTONE_REMINDER}",
        f"REOCCURRING_TROUBLE_REPORT__EXECUTION_CRON_EXPRESSION={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__EXECUTION_CRON_EXPRESSION}",
        f"REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES}",
        f"REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL}",
        f"REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD}",
        f"REOCCURRING_TROUBLE_REPORT__DEFAULT_CONTACTS={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__DEFAULT_CONTACTS}",
        f"REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_HOST_AND_CUSTOMER={SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_HOST_AND_CUSTOMER}",
        f"DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION={SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION}",
        f"DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL={SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL}",
        f"DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS_PER_HOST={SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS_PER_HOST}",
        f"DAILY_BANDWIDTH_REPORT__RECIPIENTS={SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__RECIPIENTS}",
    ]

for host in TNBA_MONITOR__MONITORED_VELOCLOUD_HOSTS:
    filename = f'env-tnba-{host.replace(".", "-")}'
    env_dict[os.path.join("services", "tnba-monitor", "src", "config", filename)] = [
        f"ENVIRONMENT_NAME={ENVIRONMENT_NAME}",
        f"NATS_SERVER1={NATS_SERVER1}",
        f"REDIS_HOSTNAME={REDIS_HOSTNAME}",
        f"CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}",
        f"PAPERTRAIL_ACTIVE={PAPERTRAIL_ACTIVE}",
        f"PAPERTRAIL_HOST={PAPERTRAIL_HOST}",
        f"PAPERTRAIL_PORT={PAPERTRAIL_PORT}",
        f"TIMEZONE={TIMEZONE}",
        f"VELOCLOUD_HOST={host}",
        f"IPA_SYSTEM_USERNAME_IN_BRUIN={IPA_SYSTEM_USERNAME_IN_BRUIN}",
        f"METRICS_RELEVANT_CLIENTS={METRICS_RELEVANT_CLIENTS}",
        f"MONITORING_JOB_INTERVAL={TNBA_MONITOR__MONITORING_JOB_INTERVAL}",
        f"MONITORED_PRODUCT_CATEGORY={TNBA_MONITOR__MONITORED_PRODUCT_CATEGORY}",
        f"BLACKLISTED_EDGES={TNBA_MONITOR__BLACKLISTED_EDGES}",
        f"GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES={TNBA_MONITOR__GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES}",
        f"GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE={TNBA_MONITOR__GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE}",
        f"MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS={TNBA_MONITOR__MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS}",
        f"SERVICE_AFFECTING__AUTORESOLVE_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__AUTORESOLVE_LOOKUP_INTERVAL}",
        f"SERVICE_AFFECTING__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL={SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL}",
        f"SERVICE_AFFECTING__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD}",
        f"SERVICE_AFFECTING__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD={SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD}",
        f"SERVICE_AFFECTING__LATENCY_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_THRESHOLD}",
        f"SERVICE_AFFECTING__PACKET_LOSS_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_THRESHOLD}",
        f"SERVICE_AFFECTING__JITTER_MONITORING_THRESHOLD={SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_THRESHOLD}",
    ]

project_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

for file_path, file_content in env_dict.items():
    print(f"Creating file {file_path}")
    with open(os.path.join(project_path, file_path), "w+") as env_file:
        env_file.write(os.linesep.join(file_content))

print("Finished creating environment files")
