import os

#Username: read_token_environment_variables_creation
#Token: nutcii_MeXfzV4HZAcdp


#VELOCLOUD_CREDENTIALS_DEV = mettel.velocloud.net+mettel@intelygenz.com+ZFAoW7iSSOOZTxNLGCpH6kFQp77fut;metvco03.mettel.net+mettel@intelygenz.com+54533hNL0qOYz6RsmITwESbvZp5jSj;metvco04.mettel.net+mettel@intelygenz.com+S4ru5K6rRkIwCMAkUYSmDvkVT41hMm
#NATS_CLUSTER_NAME = automation-engine-nats
#
#MONITORING_SECONDS = 1200
#EMAIL_ACC_PWD = xpwooxoyqwvtlqjk
#
#LAST_CONTACT_RECIPIENT_DEV = mettel@intelygenz.com
#BRUIN_CLIENT_ID_PRO = fPNu1rxOo63zpsYZVpB65Kf72485FdLD
#BRUIN_CLIENT_SECRET_PRO = Kj376v5LJatMvndcJ4g2vP5Qff8azMQxaw0brYO3eW1wJUuqtIDg4hT17XsJGq04
#BRUIN_LOGIN_URL_PRO = https://id.bruin.com/
#BRUIN_BASE_URL_PRO = https://api.bruin.com/
#
#GRAFANA_ADMIN_USER = admin
#GRAFANA_ADMIN_PASSWORD = q1w2e3r4


# Bruin variables
BRUIN_CLIENT_ID     = 'nKspuG4s32mrN0Km0WYsbRlv7M4IWfuT'
BRUIN_CLIENT_SECRET = 'sv5j5OFgoyyfbwWxOM3wJ0JTWqEqTMQ9Rrxwu7sQFIMt3O80ci0hqM2xYSh1K0Kb'
BRUIN_LOGIN_URL     = 'https://id.bruin.com/'
BRUIN_BASE_URL      = 'https://api.bruin.com/'

# Mail variables
EMAIL_ACC_PWD          = 'zyrkgturiazcfigm'
LAST_CONTACT_RECIPIENT = 'mettel@intelygenz.com'

# Nats variables
NATS_SERVER1       = 'nats://nats-server:4222'
NATS_CLUSTER_NAME  = 'automation-engine-nats'
NATSROUTECLUSTER   = 'nats://nats-server:5222'
NATSCLUSTER1       = 'nats://nats-server:5222'
NATSCLUSTER2       = 'nats://nats-server-1:5223'
NATSCLUSTER3       = 'nats://nats-server-2:5224'
NATS_PORT1         = 4222
NATS_PORT2         = 4223
NATS_PORT3         = 4224
NATS_CLUSTER_MODE1 = 's'
NATS_CLUSTER_MODE2 = 'n'
NATS_CLUSTER_MODE3 = 'n'

# Redis variables
REDIS_HOSTNAME = 'redis'

# Slack variables
SLACK_URL = 'https://hooks.slack.com/services/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'

# T7 variables
T7_BASE_URL = 'adfadf'
T7_TOKEN    = 'adfafd'

# Velocloud variables
VELOCLOUD_CREDENTIALS = ('mettel.velocloud.net+mettel@intelygenz.com+ZFAoW7iSSOOZTxNLGCpH6kFQp77fut;'
                         'metvco02.mettel.net+mettel@intelygenz.com+SvLKarWfwuvvq1AIUj7kVlnAKR34Rw;'
                         'metvco03.mettel.net+mettel@intelygenz.com+54533hNL0qOYz6RsmITwESbvZp5jSj;'
                         'metvco04.mettel.net+mettel@intelygenz.com+S4ru5K6rRkIwCMAkUYSmDvkVT41hMm')
VELOCLOUD_VERIFY_SSL  = 'yes'

# Other variables
CURRENT_ENVIRONMENT    = 'dev'
MONITORING_SECONDS     = 4500

# Getting main directory path
mettel_path = os.path.dirname(os.path.realpath(__file__))

# Creating a dict with the repos as keys and texts as values
env_dict = {
    os.path.join('base-microservice', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n',
    os.path.join('bruin-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'BRUIN_CLIENT_ID={BRUIN_CLIENT_ID}\n'
        f'BRUIN_CLIENT_SECRET={BRUIN_CLIENT_SECRET}\n'
        f'BRUIN_LOGIN_URL={BRUIN_LOGIN_URL}\n'
        f'BRUIN_BASE_URL={BRUIN_BASE_URL}',
    os.path.join('last-contact-report', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}',
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
        f'SLACK_URL={SLACK_URL}\n'
        f'EMAIL_ACC_PWD={EMAIL_ACC_PWD}',
    os.path.join('service-affecting-monitor', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}',
    os.path.join('service-outage-monitor', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}',
    os.path.join('service-outage-triage', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'CURRENT_ENVIRONMENT={CURRENT_ENVIRONMENT}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}',
    os.path.join('t7-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'T7_BASE_URL={T7_BASE_URL}\n'
        f'T7_TOKEN={T7_TOKEN}',
    os.path.join('velocloud-bridge', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'VELOCLOUD_CREDENTIALS={VELOCLOUD_CREDENTIALS}\n'
        f'VELOCLOUD_VERIFY_SSL={VELOCLOUD_VERIFY_SSL}',
    os.path.join('sites-monitor', 'src', 'config', 'env'):
        f'NATS_SERVER1={NATS_SERVER1}\n'
        f'NATS_CLUSTER_NAME={NATS_CLUSTER_NAME}\n'
        f'MONITORING_SECONDS={MONITORING_SECONDS}\n'
        f'LAST_CONTACT_RECIPIENT={LAST_CONTACT_RECIPIENT}\n'
        f'REDIS_HOSTNAME={REDIS_HOSTNAME}'    
}

# Creating all files
for file_path, envs_text in env_dict.items():
    print(f'Creating file {os.path.join(mettel_path, file_path)}')
    with open(os.path.join(mettel_path, file_path), 'w') as env_file:
        env_file.write(envs_text)
