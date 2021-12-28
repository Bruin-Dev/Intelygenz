import argparse
import gitlab
import os
import getpass

parser = argparse.ArgumentParser()
parser.add_argument('token', type=str, help='Private token to access the repo')

PRIVATE_TOKEN = parser.parse_args().token
REPO_ID = 1040
REPO_URL = f'https://gitlab.intelygenz.com'

gl = gitlab.Gitlab(REPO_URL, private_token=PRIVATE_TOKEN)
project = gl.projects.get(REPO_ID)
variables = project.variables.list(all=True)

var_dict = dict()
for v in variables:
    var_dict[v.key] = v.value

# Shared variables
TIMEZONE = var_dict["TIMEZONE"]

# Bruin variables
# We should use PRO__BRUIN_BRIDGE__TEST_* variables here, but their inventories lack lots of data in the TEST env
# so it's not worth
BRUIN_CLIENT_ID = var_dict["PRO__BRUIN_BRIDGE__CLIENT_ID"]
BRUIN_CLIENT_SECRET = var_dict["PRO__BRUIN_BRIDGE__CLIENT_SECRET"]
BRUIN_LOGIN_URL = var_dict["PRO__BRUIN_BRIDGE__LOGIN_URL"]
BRUIN_BASE_URL = var_dict["PRO__BRUIN_BRIDGE__BASE_URL"]

# customer-cache variables
CUSTOMER_CACHE__VELOCLOUD_HOSTS = var_dict["DEV__CUSTOMER_CACHE__VELOCLOUD_HOSTS"]
CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT = var_dict["DEV__CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT"]
CUSTOMER_CACHE__REFRESH_JOB_INTERVAL = var_dict["DEV__CUSTOMER_CACHE__REFRESH_JOB_INTERVAL"]
CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL = var_dict["DEV__CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL"]
CUSTOMER_CACHE__BLACKLISTED_EDGES = var_dict["DEV__CUSTOMER_CACHE__BLACKLISTED_EDGES"]
CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS = var_dict[
    "DEV__CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS"
]
CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES = var_dict["DEV__CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES"]

# DRI variables
DRI_ACC_EMAIL = var_dict["DRI_ACC_EMAIL_DEV"]
DRI_ACC_PASSWORD = var_dict["DRI_ACC_PASSWORD_DEV"]
DRI_BASE_URL = var_dict["DRI_BASE_URL_DEV"]

# DiGi variables
# DiGi DEV and TEST envs are not exposed to the world, so they're only accessable from ephemeral environments. Local
# environments can only access PRO
DIGI_CLIENT_ID = var_dict["PRO__DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_ID"]
DIGI_CLIENT_SECRET = var_dict["PRO__DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_SECRET"]
DIGI_BASE_URL = var_dict["PRO__DIGI_BRIDGE__DIGI_REBOOT_API_BASE_URL"]
DIGI_TOKEN_TTL = var_dict["PRO__DIGI_BRIDGE__DIGI_REBOOT_API_TOKEN_TTL"]

# DiGi Reboot Report variables
DIGI_REBOOT_REPORT__JOB_INTERVAL = var_dict["DEV__DIGI_REBOOT_REPORT__REPORT_JOB_INTERVAL"]
DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL = var_dict["DEV__DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL"]
DIGI_REBOOT_REPORT__RECIPIENT = var_dict["DEV__DIGI_REBOOT_REPORT__REPORT_RECIPIENT"]

# Hawkeye Affecting Monitor variables
HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL = var_dict["DEV__HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL"]
HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL = var_dict[
    "DEV__HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL"
]
HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY = var_dict[
    "DEV__HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY"
]

# Hawkeye Bridge variables
HAWKEYE_BRIDGE__CLIENT_USERNAME = var_dict["DEV__HAWKEYE_BRIDGE__CLIENT_USERNAME"]
HAWKEYE_BRIDGE__CLIENT_PASSWORD = var_dict["DEV__HAWKEYE_BRIDGE__CLIENT_PASSWORD"]
HAWKEYE_BRIDGE__BASE_URL = var_dict["DEV__HAWKEYE_BRIDGE__BASE_URL"]

# Hawkeye Customer Cache variables
HAWKEYE_CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT = var_dict[
    "DEV__HAWKEYE_CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT"
]
HAWKEYE_CUSTOMER_CACHE__REFRESH_JOB_INTERVAL = var_dict["DEV__HAWKEYE_CUSTOMER_CACHE__REFRESH_JOB_INTERVAL"]
HAWKEYE_CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES = var_dict[
    "DEV__HAWKEYE_CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES"
]

# Hawkeye Outage Monitor variables
HAWKEYE_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL = var_dict["DEV__HAWKEYE_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL"]
HAWKEYE_OUTAGE_MONITOR__QUARANTINE_FOR_DEVICES_IN_OUTAGE = var_dict[
    "DEV__HAWKEYE_OUTAGE_MONITOR__QUARANTINE_FOR_DEVICES_IN_OUTAGE"
]
HAWKEYE_OUTAGE_MONITOR__MONITORED_PRODUCT_CATEGORY = var_dict[
    "DEV__HAWKEYE_OUTAGE_MONITOR__MONITORED_PRODUCT_CATEGORY"
]
HAWKEYE_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE = var_dict[
    "DEV__HAWKEYE_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE"
]

# Cts variables
CTS_CLIENT_ID = var_dict["CTS_CLIENT_ID_DEV"]
CTS_CLIENT_SECRET = var_dict["CTS_CLIENT_SECRET_DEV"]
CTS_CLIENT_USERNAME = var_dict["CTS_CLIENT_USERNAME_DEV"]
CTS_CLIENT_PASSWORD = var_dict["CTS_CLIENT_PASSWORD_DEV"]
CTS_CLIENT_SECURITY_TOKEN = var_dict["CTS_CLIENT_SECURITY_TOKEN_DEV"]
CTS_LOGIN_URL = var_dict["CTS_LOGIN_URL_DEV"]
CTS_DOMAIN = var_dict["CTS_DOMAIN_DEV"]

# Velocloud hosts variables
VELOCLOUD_HOST_1 = var_dict["VELOCLOUD_HOST_1"]
VELOCLOUD_HOST_1_FILTER = var_dict["VELOCLOUD_HOST_1_FILTER"]
VELOCLOUD_HOST_2 = var_dict["VELOCLOUD_HOST_2"]
VELOCLOUD_HOST_2_FILTER = var_dict["VELOCLOUD_HOST_2_FILTER"]
VELOCLOUD_HOST_3 = var_dict["VELOCLOUD_HOST_3"]
VELOCLOUD_HOST_3_FILTER = var_dict["VELOCLOUD_HOST_3_FILTER"]
VELOCLOUD_HOST_4 = var_dict["VELOCLOUD_HOST_4"]
VELOCLOUD_HOST_4_FILTER = var_dict["VELOCLOUD_HOST_4_FILTER"]

# Service outage monitor hosts filter
SERVICE_OUTAGE_MONITOR_1_HOSTS = VELOCLOUD_HOST_1
SERVICE_OUTAGE_MONITOR_1_HOSTS_FILTER = VELOCLOUD_HOST_1_FILTER
SERVICE_OUTAGE_MONITOR_2_HOSTS = VELOCLOUD_HOST_2
SERVICE_OUTAGE_MONITOR_2_HOSTS_FILTER = VELOCLOUD_HOST_2_FILTER
SERVICE_OUTAGE_MONITOR_3_HOSTS = VELOCLOUD_HOST_3
SERVICE_OUTAGE_MONITOR_3_HOSTS_FILTER = VELOCLOUD_HOST_3_FILTER
SERVICE_OUTAGE_MONITOR_4_HOSTS = VELOCLOUD_HOST_4
SERVICE_OUTAGE_MONITOR_4_HOSTS_FILTER = VELOCLOUD_HOST_4_FILTER
SERVICE_OUTAGE_MONITOR_TRIAGE_HOST = ""
SERVICE_OUTAGE_MONITOR_TRIAGE_HOSTS_FILTER = []

# Lit variables
LIT_CLIENT_ID = var_dict["LIT_CLIENT_ID_DEV"]
LIT_CLIENT_SECRET = var_dict["LIT_CLIENT_SECRET_DEV"]
LIT_CLIENT_USERNAME = var_dict["LIT_CLIENT_USERNAME_DEV"]
LIT_CLIENT_PASSWORD = var_dict["LIT_CLIENT_PASSWORD_DEV"]
LIT_CLIENT_SECURITY_TOKEN = var_dict["LIT_CLIENT_SECURITY_TOKEN_DEV"]
LIT_LOGIN_URL = var_dict["LIT_LOGIN_URL_DEV"]
LIT_DOMAIN = var_dict["LIT_DOMAIN_DEV"]

# Lumin Billing Report variables
LUMIN_URI = var_dict["LUMIN_URI"]
LUMIN_TOKEN = var_dict["LUMIN_TOKEN"]
CUSTOMER_NAME = var_dict["CUSTOMER_NAME_BILLING_REPORT"]
BILLING_RECIPIENT = var_dict["BILLING_RECIPIENT_REPORT_DEV"]
EMAIL_ACC_PWD = var_dict["EMAIL_ACC_PWD"]

# Dispatch portal backend variable
DISPATCH_PORTAL_SERVER_PORT = var_dict["DISPATCH_PORTAL_SERVER_PORT"]

# Mail variables
EMAIL_ACC_PWD = var_dict["EMAIL_ACC_PWD"]
LAST_CONTACT_RECIPIENT = var_dict["LAST_CONTACT_RECIPIENT_DEV"]

# Telestax
TELESTAX_URL = var_dict["TELESTAX_URL"]
TELESTAX_ACCOUNT_SID = var_dict["TELESTAX_ACCOUNT_SID"]
TELESTAX_AUTH_TOKEN = var_dict["TELESTAX_AUTH_TOKEN"]
TELESTAX_FROM_PHONE_NUMBER = var_dict["TELESTAX_FROM_PHONE_NUMBER"]

# Nats variables
NATS_CLUSTER_NAME = var_dict["NATS_CLUSTER_NAME"]
NATS_SERVER1 = 'nats://nats-server:4222'
NATSROUTECLUSTER = 'nats://nats-server:5222'
NATSCLUSTER1 = 'nats://nats-server:5222'
NATSCLUSTER2 = 'nats://nats-server-1:5223'
NATSCLUSTER3 = 'nats://nats-server-2:5224'
NATS_PORT1 = 4222
NATS_PORT2 = 4223
NATS_PORT3 = 4224
NATS_CLUSTER_MODE1 = 's'
NATS_CLUSTER_MODE2 = 'n'
NATS_CLUSTER_MODE3 = 'n'

# Redis variables
REDIS_HOSTNAME = 'redis'
REDIS_CUSTOMER_CACHE_HOSTNAME = 'redis-customer-cache'
REDIS_TNBA_FEEDBACK_HOSTNAME = 'redis-tnba-feedback'
REDIS_EMAIL_TAGGER_HOSTNAME = 'redis-email-tagger'

# MongoDB variables
MONGODB_HOST = 'mongo'
MONGODB_USERNAME = 'root'
MONGODB_PASSWORD = 'example'
MONGODB_DATABASE = 'bruin'

# MongoDB links-metrics
MONGODB_LINKS_HOST = 'mongo-links-metrics'
MONGODB_LINKS_PORT = 27017
MONGODB_LINKS_USERNAME = 'root'
MONGODB_LINKS_PASSWORD = 'example'

# Slack variables
SLACK_URL = var_dict["SLACK_URL_DEV"]

# T7 variables
KRE_TNBA_BASE_URL = var_dict["KRE_TNBA_BASE_URL_DEV"]

# Email Tagger KRE bridge variables
EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL = var_dict["DEV__EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL"]

# Email Tagger Monitor variables
EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL = var_dict["DEV__EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL"]
EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL = var_dict["DEV__EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL"]
EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS = var_dict["DEV__EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS"]
EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS = var_dict["DEV__EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS"]
EMAIL_TAGGER_MONITOR__API_REQUEST_KEY = var_dict["DEV__EMAIL_TAGGER_MONITOR__API_REQUEST_KEY"]
EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY = var_dict[
    "DEV__EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY"
]
EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX = var_dict["DEV__EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX"]

# Velocloud variables
VELOCLOUD_CREDENTIALS = var_dict["DEV__VELOCLOUD_BRIDGE__VELOCLOUD_CREDENTIALS"]

# Ticket collector variables
INTERVAL_TASKS_RUN = 1

# Ticket stats variables
TICKET_STATS_SERVER_NAME = 'host.docker.internal'
TICKET_STATS_SERVER_PORT = 3000
TICKET_STATS_SERVER_ROOT_PATH = '/api'
TICKET_STATS_SERVER_VERSION = '1.0.0'

# Other variables
CURRENT_ENVIRONMENT = 'dev'
MONITORING_SECONDS = 4500
EXEC_MONITOR_REPORTS_ON_START = False
EXEC_BANDWIDTH_REPORTS_ON_START = False

# Getting main directory path
mettel_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir))

# Get environment name of local system
ENVIRONMENT_NAME = getpass.getuser() + '-local'

# Papertrail environment variables
PAPERTRAIL_ACTIVE = False
PAPERTRAIL_PORT = 1111
PAPERTRAIL_HOST = "logs.papertrailapp.com"

# Creating a dict with the repos as keys and texts as values
env_dict = {
    os.path.join('base-microservice', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}',
    os.path.join('services', 'bruin-bridge', 'src', 'config', 'env'):
        f'CURRENT_ENVIRONMENT={ENVIRONMENT_NAME}\n'
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'BRUIN_CLIENT_ID={BRUIN_CLIENT_ID}\n'
        f'BRUIN_CLIENT_SECRET={BRUIN_CLIENT_SECRET}\n'
        f'BRUIN_LOGIN_URL={BRUIN_LOGIN_URL}\n'
        f'BRUIN_BASE_URL={BRUIN_BASE_URL}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'digi-bridge', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'DIGI_CLIENT_ID={DIGI_CLIENT_ID}\n'
        f'DIGI_CLIENT_SECRET={DIGI_CLIENT_SECRET}\n'
        f'DIGI_BASE_URL={DIGI_BASE_URL}\n'
        f'DIGI_TOKEN_TTL={DIGI_TOKEN_TTL}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'digi-reboot-report', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'JOB_INTERVAL={DIGI_REBOOT_REPORT__JOB_INTERVAL}\n'
        f'LOGS_LOOKUP_INTERVAL={DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL}\n'
        f'RECIPIENT={DIGI_REBOOT_REPORT__RECIPIENT}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'dri-bridge', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'DRI_ACC_EMAIL={DRI_ACC_EMAIL}\n'
        f'DRI_ACC_PASSWORD={DRI_ACC_PASSWORD}\n'
        f'DRI_BASE_URL={DRI_BASE_URL}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'customer-cache', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'REDIS_CUSTOMER_CACHE_HOSTNAME={REDIS_CUSTOMER_CACHE_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'VELOCLOUD_HOSTS={CUSTOMER_CACHE__VELOCLOUD_HOSTS}\n'
        f'DUPLICATE_INVENTORIES_RECIPIENT={CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}\n'
        f'REFRESH_JOB_INTERVAL={CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}\n'
        f'REFRESH_CHECK_INTERVAL={CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL}\n'
        f'BLACKLISTED_EDGES={CUSTOMER_CACHE__BLACKLISTED_EDGES}\n'
        f'BLACKLISTED_CLIENTS_WITH_PENDING_STATUS={CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS}\n'
        f'WHITELISTED_MANAGEMENT_STATUSES={CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}',
    os.path.join('services', 'email-tagger-kre-bridge', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'KRE_BASE_URL={EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'email-tagger-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'REDIS_EMAIL_TAGGER_HOSTNAME={REDIS_EMAIL_TAGGER_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'API_REQUEST_KEY={EMAIL_TAGGER_MONITOR__API_REQUEST_KEY}\n'
        f'API_REQUEST_SIGNATURE_SECRET_KEY={EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY}\n'
        f'API_SERVER_ENDPOINT_PREFIX={EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX}\n'
        f'NEW_EMAILS_JOB_INTERVAL={EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL}\n'
        f'NEW_TICKETS_JOB_INTERVAL={EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL}\n'
        f'MAX_CONCURRENT_EMAILS={EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS}\n'
        f'MAX_CONCURRENT_TICKETS={EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'hawkeye-affecting-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'MONITORING_JOB_INTERVAL={HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL}\n'
        f'PROBES_TESTS_RESULTS_LOOKUP_INTERVAL={HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL}\n'
        f'MONITORED_PRODUCT_CATEGORY={HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'hawkeye-bridge', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CLIENT_USERNAME={HAWKEYE_BRIDGE__CLIENT_USERNAME}\n'
        f'CLIENT_PASSWORD={HAWKEYE_BRIDGE__CLIENT_PASSWORD}\n'
        f'BASE_URL={HAWKEYE_BRIDGE__BASE_URL}',
    os.path.join('services', 'hawkeye-customer-cache', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'REDIS_CUSTOMER_CACHE_HOSTNAME={REDIS_CUSTOMER_CACHE_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'DUPLICATE_INVENTORIES_RECIPIENT={HAWKEYE_CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}\n'
        f'REFRESH_JOB_INTERVAL={HAWKEYE_CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}\n'
        f'WHITELISTED_MANAGEMENT_STATUSES={HAWKEYE_CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}',
    os.path.join('services', 'hawkeye-outage-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'MONITORING_JOB_INTERVAL={HAWKEYE_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL}\n'
        f'QUARANTINE_FOR_DEVICES_IN_OUTAGE={HAWKEYE_OUTAGE_MONITOR__QUARANTINE_FOR_DEVICES_IN_OUTAGE}\n'
        f'MONITORED_PRODUCT_CATEGORY={HAWKEYE_OUTAGE_MONITOR__MONITORED_PRODUCT_CATEGORY}\n'
        f'GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE='
        f'{HAWKEYE_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE}',
    os.path.join('metrics-dashboard', 'grafana', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}',
    os.path.join('services', 'last-contact-report', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}',
    os.path.join('services', 'lumin-billing-report', 'src', 'config', 'env'):
        f'LUMIN_URI={LUMIN_URI}\n'
        f'LUMIN_TOKEN={LUMIN_TOKEN}\n'
        f'CUSTOMER_NAME={CUSTOMER_NAME}\n'
        f'BILLING_RECIPIENT={BILLING_RECIPIENT}\n'
        f'EMAIL_ACC_PWD={EMAIL_ACC_PWD}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('nats-server', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CLUSTER_MODE={NATS_CLUSTER_MODE1}\n'
        f'NATSCLUSTER={NATSCLUSTER1}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'PORT={NATS_PORT1}',
    os.path.join('nats-server', 'nats-server-1-env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CLUSTER_MODE={NATS_CLUSTER_MODE2}\n'
        f'NATSCLUSTER={NATSCLUSTER2}\n'
        f'NATSROUTECLUSTER={NATSROUTECLUSTER}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'PORT={NATS_PORT2}',
    os.path.join('nats-server', 'nats-server-2-env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CLUSTER_MODE={NATS_CLUSTER_MODE3}\n'
        f'NATSCLUSTER={NATSCLUSTER3}\n'
        f'NATSROUTECLUSTER={NATSROUTECLUSTER}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'PORT={NATS_PORT3}',
    os.path.join('services', 'notifier', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'SLACK_URL={SLACK_URL}\n'
        f'TELESTAX_URL={TELESTAX_URL}\n'
        f'TELESTAX_ACCOUNT_SID={TELESTAX_ACCOUNT_SID}\n'
        f'TELESTAX_AUTH_TOKEN={TELESTAX_AUTH_TOKEN}\n'
        f'TELESTAX_FROM_PHONE_NUMBER={TELESTAX_FROM_PHONE_NUMBER}\n'
        f'EMAIL_ACC_PWD={EMAIL_ACC_PWD}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'service-affecting-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'EXEC_MONITOR_REPORTS_ON_START={EXEC_MONITOR_REPORTS_ON_START}\n'
        f'EXEC_BANDWIDTH_REPORTS_ON_START={EXEC_BANDWIDTH_REPORTS_ON_START}',
    os.path.join('services', 'service-outage-monitor', 'src', 'config', 'env-outage-monitor-1'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_1_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_1_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'service-outage-monitor', 'src', 'config', 'env-outage-monitor-2'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_2_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_2_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'service-outage-monitor', 'src', 'config', 'env-outage-monitor-3'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_3_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_3_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'service-outage-monitor', 'src', 'config', 'env-outage-monitor-4'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_4_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_4_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'service-outage-monitor', 'src', 'config', 'env-triage'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_TRIAGE_HOST}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_TRIAGE_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=1\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'sites-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'MONITORING_SECONDS={MONITORING_SECONDS}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 't7-bridge', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'KRE_BASE_URL={KRE_TNBA_BASE_URL}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'velocloud-bridge', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'VELOCLOUD_CREDENTIALS={VELOCLOUD_CREDENTIALS}\n'
        f'TIMEZONE={TIMEZONE}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'tnba-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'tnba-feedback', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'REDIS_TNBA_FEEDBACK_HOSTNAME={REDIS_TNBA_FEEDBACK_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'intermapper-outage-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'ticket-collector', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'MONGODB_HOST={MONGODB_HOST}\n'
        f'MONGODB_USERNAME={MONGODB_USERNAME}\n'
        f'MONGODB_PASSWORD={MONGODB_PASSWORD}\n'
        f'MONGODB_DATABASE={MONGODB_DATABASE}\n'
        f'BRUIN_CLIENT_ID={BRUIN_CLIENT_ID}\n'
        f'BRUIN_CLIENT_SECRET={BRUIN_CLIENT_SECRET}\n'
        f'INTERVAL_TASKS_RUN={INTERVAL_TASKS_RUN}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'ticket-statistics', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'MONGODB_HOST={MONGODB_HOST}\n'
        f'MONGODB_USERNAME={MONGODB_USERNAME}\n'
        f'MONGODB_PASSWORD={MONGODB_PASSWORD}\n'
        f'MONGODB_DATABASE={MONGODB_DATABASE}\n'
        f'SERVER_NAME={TICKET_STATS_SERVER_NAME}\n'
        f'SERVER_PORT={TICKET_STATS_SERVER_PORT}\n'
        f'SERVER_ROOT_PATH={TICKET_STATS_SERVER_ROOT_PATH}\n'
        f'SERVER_VERSION={TICKET_STATS_SERVER_VERSION}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}',
    os.path.join('services', 'links-metrics-collector', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'MONGO_URL={MONGODB_LINKS_HOST}\n'
        f'MONGO_USERNAME={MONGODB_USERNAME}\n'
        f'MONGO_PASS={MONGODB_LINKS_USERNAME}\n'
        f'MONGO_PORT={MONGODB_DATABASE}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'links-metrics-api', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'MONGO_URL={MONGODB_LINKS_HOST}\n'
        f'MONGO_USERNAME={MONGODB_USERNAME}\n'
        f'MONGO_PASS={MONGODB_LINKS_USERNAME}\n'
        f'MONGO_PORT={MONGODB_DATABASE}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
    os.path.join('services', 'fraud-monitor', 'src', 'config', 'env'):
        f'ENVIRONMENT_NAME={ENVIRONMENT_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'PAPERTRAIL_ACTIVE=False\n'
        f'PAPERTRAIL_HOST={PAPERTRAIL_HOST}\n'
        f'PAPERTRAIL_PORT={PAPERTRAIL_PORT}',
}

# Creating all files
for file_path, envs_text in env_dict.items():
    print(f'Creating file {os.path.join(mettel_path, file_path)}')
    with open(os.path.join(mettel_path, file_path), 'w') as env_file:
        env_file.write(envs_text)
