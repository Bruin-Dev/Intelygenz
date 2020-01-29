import argparse
import gitlab
import os

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

# Bruin variables
BRUIN_CLIENT_ID = var_dict["BRUIN_CLIENT_ID_PRO"]
BRUIN_CLIENT_SECRET = var_dict["BRUIN_CLIENT_SECRET_PRO"]
BRUIN_LOGIN_URL = var_dict["BRUIN_LOGIN_URL_PRO"]
BRUIN_BASE_URL = var_dict["BRUIN_BASE_URL_PRO"]

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

# Dispatch portal backend variable
DISPATCH_PORTAL_SERVER_PORT = var_dict["DISPATCH_PORTAL_SERVER_PORT"]

# Mail variables
EMAIL_ACC_PWD = var_dict["EMAIL_ACC_PWD"]
LAST_CONTACT_RECIPIENT = var_dict["LAST_CONTACT_RECIPIENT_DEV"]

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

# Slack variables
SLACK_URL = var_dict["SLACK_URL_DEV"]

# T7 variables
T7_BASE_URL = var_dict["T7_BASE_URL_DEV"]
T7_TOKEN = var_dict["T7_TOKEN_DEV"]

# Velocloud variables
VELOCLOUD_CREDENTIALS = var_dict["VELOCLOUD_CREDENTIALS_DEV"]
VELOCLOUD_VERIFY_SSL = 'yes'

# Other variables
CURRENT_ENVIRONMENT = 'dev'
MONITORING_SECONDS = 4500

# Getting main directory path
mettel_path = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), os.pardir))

# Creating a dict with the repos as keys and texts as values
env_dict = {
    os.path.join('base-microservice', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}',
    os.path.join('bruin-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'BRUIN_CLIENT_ID={BRUIN_CLIENT_ID}\n'
        f'BRUIN_CLIENT_SECRET={BRUIN_CLIENT_SECRET}\n'
        f'BRUIN_LOGIN_URL={BRUIN_LOGIN_URL}\n'
        f'BRUIN_BASE_URL={BRUIN_BASE_URL}',
    os.path.join('cts-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'CTS_CLIENT_ID={CTS_CLIENT_ID}\n'
        f'CTS_CLIENT_SECRET={CTS_CLIENT_SECRET}\n'
        f'CTS_CLIENT_USERNAME={CTS_CLIENT_USERNAME}\n'
        f'CTS_CLIENT_PASSWORD={CTS_CLIENT_PASSWORD}\n'
        f'CTS_CLIENT_SECURITY_TOKEN={CTS_CLIENT_SECURITY_TOKEN}\n'
        f'CTS_LOGIN_URL={CTS_LOGIN_URL}\n'
        f'CTS_DOMAIN={CTS_DOMAIN}\n',
    os.path.join('dispatch-portal-backend', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'DISPATCH_PORTAL_SERVER_PORT={DISPATCH_PORTAL_SERVER_PORT}',
    os.path.join('metrics-dashboard', 'grafana', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}',
    os.path.join('last-contact-report', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}',
    os.path.join('lit-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'LIT_CLIENT_ID={LIT_CLIENT_ID}\n'
        f'LIT_CLIENT_SECRET={LIT_CLIENT_SECRET}\n'
        f'LIT_CLIENT_USERNAME={LIT_CLIENT_USERNAME}\n'
        f'LIT_CLIENT_PASSWORD={LIT_CLIENT_PASSWORD}\n'
        f'LIT_CLIENT_SECURITY_TOKEN={LIT_CLIENT_SECURITY_TOKEN}\n'
        f'LIT_LOGIN_URL={LIT_LOGIN_URL}\n'
        f'LIT_DOMAIN={LIT_DOMAIN}\n',
    os.path.join('nats-server', 'env'):
        f'CLUSTER_MODE={NATS_CLUSTER_MODE1}\n'
        f'NATSCLUSTER={NATSCLUSTER1}\n'
        f'PORT={NATS_PORT1}',
    os.path.join('nats-server', 'nats-server-1-env'):
        f'CLUSTER_MODE={NATS_CLUSTER_MODE2}\n'
        f'NATSCLUSTER={NATSCLUSTER2}\n'
        f'NATSROUTECLUSTER={NATSROUTECLUSTER}\n'
        f'PORT={NATS_PORT2}',
    os.path.join('nats-server', 'nats-server-2-env'):
        f'CLUSTER_MODE={NATS_CLUSTER_MODE3}\n'
        f'NATSCLUSTER={NATSCLUSTER3}\n'
        f'NATSROUTECLUSTER={NATSROUTECLUSTER}\n'
        f'PORT={NATS_PORT3}',
    os.path.join('notifier', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'SLACK_URL={SLACK_URL}\n'
        f'EMAIL_ACC_PWD={EMAIL_ACC_PWD}',
    os.path.join('service-affecting-monitor', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}',
    os.path.join('service-outage-monitor', 'src', 'config', 'env-outage-monitor-1'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_1_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_1_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0',
    os.path.join('service-outage-monitor', 'src', 'config', 'env-outage-monitor-2'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_2_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_2_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0',
    os.path.join('service-outage-monitor', 'src', 'config', 'env-outage-monitor-3'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_3_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_3_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0',
    os.path.join('service-outage-monitor', 'src', 'config', 'env-outage-monitor-4'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_4_HOSTS}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_4_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=0',
    os.path.join('service-outage-monitor', 'src', 'config', 'env-triage'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'VELOCLOUD_HOSTS={SERVICE_OUTAGE_MONITOR_TRIAGE_HOST}\n'
        f'VELOCLOUD_HOSTS_FILTER={SERVICE_OUTAGE_MONITOR_TRIAGE_HOSTS_FILTER}\n'
        f'ENABLE_TRIAGE_MONITORING=1',
    os.path.join('t7-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'T7_BASE_URL={T7_BASE_URL}\n'
        f'T7_TOKEN={T7_TOKEN}',
    os.path.join('velocloud-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}\n'
        f'VELOCLOUD_CREDENTIALS={VELOCLOUD_CREDENTIALS}\n'
        f'VELOCLOUD_VERIFY_SSL={VELOCLOUD_VERIFY_SSL}',
    os.path.join('sites-monitor', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'MONITORING_SECONDS={MONITORING_SECONDS}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}',
    os.path.join('tnba-monitor', 'src', 'config', 'env'):
            f'NATS_SERVER1={NATS_SERVER1}\n'
            f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
            f'REDIS_HOSTNAME={REDIS_HOSTNAME}'
}

# Creating all files
for file_path, envs_text in env_dict.items():
    print(f'Creating file {os.path.join(mettel_path, file_path)}')
    with open(os.path.join(mettel_path, file_path), 'w') as env_file:
        env_file.write(envs_text)
