# Default values for bruin-bridge.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

# -- Number of bruin-bridge pods to do calls to Bruin API.
# Do not set this below 2 unless is going to deploy in dev or local environment.
replicaCount: 1

# -- nats helm chart configuration
nats:
  cluster:
    enabled: true
  natsbox:
    enabled: false
  # -- override name to use nats as name for svc, deployment and all created by nats helm chart
  nameOverride: "nats"


## YAML anchor to define capabilities_enabled
.capabilitiesEnabled: &capabilitiesEnabled
  capabilities_enabled:
    # -- Indicate if bruin-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # bruin-bridge service responds correctly to healthcheck calls.
    bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
    # -- Indicate if cts-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # cts-bridge service responds correctly to healthcheck calls.
    cts_bridge: ${CTS_BRIDGE_ENABLED}
    # -- Indicate if digi-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # digi-bridge service responds correctly to healthcheck calls.
    digi_bridge: ${DIGI_BRIDGE_ENABLED}
    # -- Indicate if email-tagger-kre-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # email-tagger-kre-bridge service responds correctly to healthcheck calls.
    email_tagger_kre_bridge: ${EMAIL_TAGGER_KRE_BRIDGE_ENABLED}
    # -- Indicate if hawkeye-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # hawkeye-bridge service responds correctly to healthcheck calls.
    hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
    # -- Indicate if lit-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # lit-bridge service responds correctly to healthcheck calls.
    lit_bridge: ${LIT_BRIDGE_ENABLED}
    # -- Indicate if notifier is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # notifier service responds correctly to healthcheck calls.
    notifier: ${NOTIFIER_ENABLED}
    # -- Indicate if t7-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # t7-bridge service responds correctly to healthcheck calls.
    t7_bridge: ${T7_BRIDGE_ENABLED}
    # -- Indicate if velocloud-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # velocloud-bridge service responds correctly to healthcheck calls.
    velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}


# -- Global configuration for all subcharts
global:
  # -- Name of environment for EKS cluster and network resources
  current_environment: ${CURRENT_ENVIRONMENT}
  # -- Name of environment for helm charts
  environment: "${ENVIRONMENT_SLUG}"
  # -- NATS cluster endpoint used by bruin-bridge
  nats_server: "nats://nats:4222"
  # -- Redis Hostname used to store heavy NATS messages (>1MB)
  redis_hostname: ${REDIS_HOSTNAME}
  # -- Redis hostname used to store information used by customer-cache
  redis_customer_cache_hostname: ${REDIS_CUSTOMER_CACHE_HOSTNAME}
  # -- Redis Hostname used to store metrics obtained from tnba-feedback to train the ML model
  redis_tnba_feedback_hostname: ${REDIS_TNBA_FEEDBACK_HOSTNAME}
  # -- Redis Hostname used to store information used by email-tagger
  redis_email_tagger_hostname: ${REDIS_EMAIL_TAGGER_HOSTNAME}
  # -- Indicates if the logs will be sent to papertrail or not.
  papertrail_active: ${PAPERTRAIL_ACTIVE}
  # -- Papertrail host to which the logs will be sent
  papertrail_host: ${PAPERTRAIL_HOST}
  # -- Papertrail port to which the logs will be sent
  papertrail_port: ${PAPERTRAIL_PORT}
  # -- Contact email address
  last_contact_recipient: ${LAST_CONTACT_RECIPIENT}
  # -- Email account password
  email_acc_pwd: ${EMAIL_ACC_PWD}
  # -- Indicates if the helm chart will be displayed in an aws or local environment,
  # in case it is local, a specific imagePullSecret will be used to access the images stored in ECR.
  mode: "aws"
  ecr_registry:
    # -- Name of the imagePullSecret created to access the images stored in ECR.
    name: "ecr-registry"


# -- bruin-bridge subchart specific configuration
bruin-bridge:
  # -- Field to indicate if the bruin-bridge module is going to be deployed
  enabled: ${BRUIN_BRIDGE_ENABLED}
  # -- Number of bruin-bridge pods to do calls to Bruin API.
  # Do not set this below 2 unless is going to deploy in dev or local environment.
  replicaCount: ${BRUIN_BRIDGE_DESIRED_TASKS}
  image:
    # -- Repository image for bruin-bridge module
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/bruin-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${BRUIN_BRIDGE_BUILD_NUMBER}
  # -- Service Configuration
  service:
    type: ClusterIP
    port: 5000
  # bruin-bridge specific configuration variables
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "bruin-bridge-${BRUIN_BRIDGE_BUILD_NUMBER}"
    # -- Client ID credentials for Bruin API
    bruin_client_id: ${BRUIN_CLIENT_ID}
    # -- Client Secret credentials for Bruin API
    bruin_client_secret: ${BRUIN_CLIENT_SECRET}
    # -- IP of Bruin Login URL (needed only in dev environments)
    bruin_login_url_ip: ${BRUIN_LOGIN_URL_IP}
    # -- Login URL for Bruin API
    bruin_login_url: ${BRUIN_LOGIN_URL}
    # -- Base URL for Bruin API (needed only in dev environments)
    bruin_base_url_ip: ${BRUIN_BASE_URL_IP}
    # -- Base URL for Bruin API
    bruin_base_url: ${BRUIN_BASE_URL}
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- cts-bridge subchart specific configuration
cts-bridge:
  replicaCount: ${CTS_BRIDGE_DESIRED_TASKS}
  # -- Field to indicate if the cts-bridge module is going to be deployed
  enabled: ${CTS_BRIDGE_ENABLED}
  # cts-bridge specific configuration variables
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "cts-bridge-${CTS_BRIDGE_BUILD_NUMBER}"
    # -- Client ID credentials for CTS API
    cts_client_id: ${CTS_CLIENT_ID}
    # -- Client Secret credentials for CTS API
    cts_client_secret: ${CTS_CLIENT_SECRET}
    # -- Username credentials for CTS API
    cts_client_username: ${CTS_CLIENT_USERNAME}
    # -- Password credentials for CTS API
    cts_client_password: ${CTS_CLIENT_PASSWORD}
    # -- Security Token credentials for CTS API
    cts_client_security_token: ${CTS_CLIENT_SECURITY_TOKEN}
    # -- Login URL for CTS API
    cts_login_url: ${CTS_LOGIN_URL}
    # -- Domain URL for CTS API
    cts_domain: ${CTS_DOMAIN}
  # -- cts-bridge image details
  image:
    # -- cts-bridge
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/cts-bridge
    pullPolicy: Always
    # -- cts-bridge tag of docker image
    tag: ${CTS_BRIDGE_BUILD_NUMBER}
  # -- cts-bridge service details
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${CTS_BRIDGE_ENABLED}
    minReplicas: ${CTS_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- customer-cache subchart specific configuration
customer-cache:
  enabled: ${CUSTOMER_CACHE_ENABLED}
  replicaCount: ${CUSTOMER_CACHE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "customer-cache-${CUSTOMER_CACHE_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/customer-cache
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${CUSTOMER_CACHE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- digi-bridge subchart specific configuration
digi-bridge:
  # -- Field to indicate if the digi-bridge module is going to be deployed
  enabled: ${DIGI_BRIDGE_ENABLED}
  replicaCount: ${DIGI_BRIDGE_DESIRED_TASKS}
  # digi-bridge specific configuration variables
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "digi-bridge-${DIGI_BRIDGE_BUILD_NUMBER}"
    # -- Client ID credentials for Digi API
    digi_client_id: ${DIGI_CLIENT_ID}
    # -- Client Secret credentials for Digi API
    digi_client_secret: ${DIGI_CLIENT_SECRET}
    # -- Base URL for Digi API
    digi_base_url: ${DIGI_BASE_URL}
    # -- IP for Digi Production Environment
    digi_ip_pro: ${DIGI_IP_PRO}
    # -- Record name for Digi Production Environment
    digi_record_name_pro: ${DIGI_RECORD_NAME_PRO}
    # -- IP for Digi Dev Environment
    digi_ip_dev: ${DIGI_IP_DEV}
    # -- Record name for Digi Dev Environment
    digi_record_name_dev: ${DIGI_RECORD_NAME_DEV}
    # -- IP for Digi Test Environment
    digi_ip_test: ${DIGI_IP_TEST}
    # -- Record name for Digi Test Environment
    digi_record_name_test: ${DIGI_RECORD_NAME_TEST}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/digi-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${DIGI_BRIDGE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${DIGI_BRIDGE_ENABLED}
    minReplicas: ${DIGI_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- digi-reboot-report subchart specific configuration
digi-reboot-report:
  enabled: ${DIGI_REBOOT_REPORT_ENABLED}
  replicaCount: ${DIGI_REBOOT_REPORT_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "digi-reboot-report-${DIGI_REBOOT_REPORT_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    # -- Email address to send digi-reboot-report
    digi_report_recipient: ${DIGI_REPORT_RECIPIENT}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/digi-reboot-report
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${DIGI_REBOOT_REPORT_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- dispatch-portal-backend subchart specific configuration
dispatch-portal-backend:
  enabled: ${DISPATCH_PORTAL_BACKEND_ENABLED}
  replicaCount: ${DISPATCH_PORTAL_BACKEND_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "dispatch-portal-backend-${DISPATCH_PORTAL_BACKEND_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    dispatch_portal_server_port: 5000
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/dispatch-portal-backend
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${DISPATCH_PORTAL_BACKEND_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- dispatch-portal-frontend subchart specific configuration
dispatch-portal-frontend:
  enabled: ${DISPATCH_PORTAL_FRONTEND_ENABLED}
  replicaCount: ${DISPATCH_PORTAL_FRONTEND_DESIRED_TASKS}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/dispatch-portal-frontend
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${DISPATCH_PORTAL_FRONTEND_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- email-tagger-kre-bridge subchart specific configuration
email-tagger-kre-bridge:
  enabled: ${EMAIL_TAGGER_KRE_BRIDGE_ENABLED}
  replicaCount: ${EMAIL_TAGGER_KRE_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "email-tagger-kre-bridge-${EMAIL_TAGGER_KRE_BRIDGE_BUILD_NUMBER}"
    # -- Base URL for KRE API
    kre_base_url: ${KRE_EMAIL_TAGGER_BASE_URL}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/email-tagger-kre-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${EMAIL_TAGGER_KRE_BRIDGE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${EMAIL_TAGGER_KRE_BRIDGE_ENABLED}
    minReplicas: ${EMAIL_TAGGER_KRE_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- email-tagger-monitor subchart specific configuration
email-tagger-monitor:
  enabled: ${EMAIL_TAGGER_MONITOR_ENABLED}
  replicaCount: ${EMAIL_TAGGER_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "email-tagger-monitor-${EMAIL_TAGGER_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    # -- Signature secret key
    request_signature_secret_key: ${REQUEST_SIGNATURE_SECRET_KEY}
    # -- Request api key
    request_api_key: ${REQUEST_API_KEY}
    # -- API server endpoint prefix
    api_server_endpoint_prefix: "/api/email-tagger-webhook"
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/email-tagger-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${EMAIL_TAGGER_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- hawkeye-affecting-monitor subchart specific configuration
hawkeye-affecting-monitor:
  enabled: ${HAWKEYE_AFFECTING_MONITOR_ENABLED}
  replicaCount: ${HAWKEYE_AFFECTING_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "hawkeye-affecting-monitor-${HAWKEYE_AFFECTING_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-affecting-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${HAWKEYE_AFFECTING_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- hawkeye-bridge subchart specific configuration
hawkeye-bridge:
  enabled: ${HAWKEYE_BRIDGE_ENABLED}
  replicaCount: ${HAWKEYE_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "hawkeye-bridge-${HAWKEYE_BRIDGE_BUILD_NUMBER}"
    hawkeye_client_username: ${HAWKEYE_CLIENT_USERNAME}
    # -- Client password credentials for Hawkeye API
    hawkeye_client_password: ${HAWKEYE_CLIENT_PASSWORD}
    ## -- Base URL for Hawkeye API
    hawkeye_base_url: ${HAWKEYE_BASE_URL}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${HAWKEYE_BRIDGE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${HAWKEYE_BRIDGE_ENABLED}
    minReplicas: ${HAWKEYE_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- hawkeye-customer-cache specific configuration
hawkeye-customer-cache:
  enabled: ${HAWKEYE_CUSTOMER_CACHE_ENABLED}
  replicaCount: ${HAWKEYE_CUSTOMER_CACHE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "hawkeye-customer-cache-${HAWKEYE_CUSTOMER_CACHE_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-customer-cache
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${HAWKEYE_CUSTOMER_CACHE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- hawkeye-outage-monitor subchart specific configuration
hawkeye-outage-monitor:
  enabled: ${HAWKEYE_OUTAGE_MONITOR_ENABLED}
  replicaCount: ${HAWKEYE_OUTAGE_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "hawkeye-outage-monitor-${HAWKEYE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/hawkeye-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${HAWKEYE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi

# -- intermapper-outage-monitor subchart specific configuration
intermapper-outage-monitor:
  enabled: ${INTERMAPPER_OUTAGE_MONITOR_ENABLED}
  replicaCount: ${INTERMAPPER_OUTAGE_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "intermapper-outage-monitor-${INTERMAPPER_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/intermapper-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${INTERMAPPER_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi

# -- last-contact-report subchart specific configuration
last-contact-report:
  enabled: ${LAST_CONTACT_REPORT_ENABLED}
  replicaCount: ${LAST_CONTACT_REPORT_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "last-contact-report-${LAST_CONTACT_REPORT_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/last-contact-report
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${LAST_CONTACT_REPORT_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- links-metrics-api subchart specific configuration
links-metrics-api:
  enabled: ${LINKS_METRICS_API_ENABLED}
  # -- Number of links-metrics-api pods
  replicaCount: ${LINKS_METRICS_API_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "links-metrics-api-${LINKS_METRICS_API_BUILD_NUMBER}"
    # -- Indicate mongo username    
    mongodb_username: ${TICKET_COLLECTOR_MONGO_USERNAME}
    # -- Indicate mongo password
    mongodb_password: ${TICKET_COLLECTOR_MONGO_PASSWORD}
    # -- Indicate mongo hostname
    mongodb_host: ${TICKET_COLLECTOR_MONGO_HOST}
    # -- Indicate mongo port to use
    mongodb_port: ${TICKET_COLLECTOR_MONGO_PORT}
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/links-metrics-api
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${LINKS_METRICS_API_BUILD_NUMBER}
  service:
    type: LoadBalancer
    port: 5000
    securityGroup: ${OREILLY_SECURITY_GROUP_ID}
    awsCertArn: ${AUTOMATION_SSL_CERTIFICATE_ARN}
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- links-metrics-collector subchart specific configuration
links-metrics-collector:
  enabled: ${LINKS_METRICS_COLLECTOR_ENABLED}
  # -- Number of links-metrics-api pods
  replicaCount: ${LINKS_METRICS_COLLECTOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "links-metrics-api-${LINKS_METRICS_COLLECTOR_BUILD_NUMBER}"
    # -- Indicate mongo username    
    mongodb_username: ${TICKET_COLLECTOR_MONGO_USERNAME}
    # -- Indicate mongo password
    mongodb_password: ${TICKET_COLLECTOR_MONGO_PASSWORD}
    # -- Indicate mongo hostname
    mongodb_host: ${TICKET_COLLECTOR_MONGO_HOST}
    # -- Indicate mongo port to use
    mongodb_port: ${TICKET_COLLECTOR_MONGO_PORT}
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/links-metrics-collector
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${LINKS_METRICS_COLLECTOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 400m
      memory: 512Mi
    requests:
      cpu: 200m
      memory: 256Mi


# -- lit-bridge subchart specific configuration
lit-bridge:
  enabled: ${LIT_BRIDGE_ENABLED}
  # -- Number of lit-bridge pods to do calls to LIT API.
  replicaCount: ${LIT_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "lit-bridge-${LIT_BRIDGE_BUILD_NUMBER}"
    # -- Client ID credentials for LIT API
    lit_client_id: ${LIT_CLIENT_ID}
    # -- Client Secret credentials for LIT API
    lit_client_secret: ${LIT_CLIENT_SECRET
    # -- Username credentials for LIT API
    lit_client_username: ${LIT_CLIENT_USERNAME}
    # -- Password credentials for LIT API
    lit_client_password: ${LIT_CLIENT_PASSWORD}
    # -- Security token credentials for LIT API
    lit_client_security_token: ${LIT_CLIENT_SECURITY_TOKEN}
    # -- Login URL for LIT API
    lit_login_url: ${LIT_LOGIN_URL}
    # -- Domain for LIT API
    lit_domain: ${LIT_DOMAIN}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/lit-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${LIT_BRIDGE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${LIT_BRIDGE_ENABLED}
    minReplicas: ${LIT_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- lumin-billing-report subchart specific configuration
lumin-billing-report:
  enabled: ${LUMIN_BILLING_REPORT_ENABLED}
  replicaCount: ${LUMIN_BILLING_REPORT_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "lumin-billing-report-${LUMIN_BILLING_REPORT_BUILD_NUMBER}"
    # -- URI of Lumin API
    lumin_uri: ${LUMIN_URI}
    # -- Token credentials for Lumin API
    lumin_token: ${LUMIN_TOKEN}
    # -- Name of customer to generate lumin-billing-report
    customer_name: ${CUSTOMER_NAME_BILLING_REPORT}
    # -- Email address to send lumin-billing-report
    billing_recipient: ${BILLING_RECIPIENT}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/lumin-billing-report
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${LUMIN_BILLING_REPORT_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- notifier subchart specific configuration
notifier:
  enabled: ${NOTIFIER_ENABLED}
  replicaCount: ${NOTIFIER_DESIRED_TASKS}
  # -- notifier image details
  image:
    # -- notifier repository for docker images
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/notifier
    pullPolicy: Always
    # -- notifier tag of docker image
    tag: ${NOTIFIER_BUILD_NUMBER}
  # -- notifier Service Configuration
  service:
    type: ClusterIP
    port: 5000
  # notifier specific configuration variables
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "notifier-${NOTIFIER_BUILD_NUMBER}"
    # -- Slack Webhook URL to send messages
    slack_url: ${NOTIFIER_SLACK_URL}
    # -- Telestax URL
    telestax_url: ${TELESTAX_URL}
    # -- Telestax account SID
    telestax_account_sid: ${TELESTAX_ACCOUNT_SID}
    # -- Telestax auth token credentials
    telestax_auth_token: ${TELESTAX_AUTH_TOKEN}
    telestax_from_phone_number: ${TELESTAX_FROM_PHONE_NUMBER}
  resources:
    # We usually recommend not to specify default resources and to leave this as a conscious
    # choice for the user. This also increases chances charts run on environments with little
    # resources, such as Minikube. If you do want to specify resources, uncomment the following
    # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${NOTIFIER_ENABLED}
    minReplicas: ${NOTIFIER_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- service-affecting-monitor subchart specific configuration
service-affecting-monitor:
  enabled: ${SERVICE_AFFECTING_MONITOR_ENABLED}
  replicaCount: ${SERVICE_AFFECTING_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-affecting-monitor-${SERVICE_AFFECTING_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-affecting-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_AFFECTING_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- service-dispatch-monitor subchart specific configuration
service-dispatch-monitor:
  enabled: ${SERVICE_DISPATCH_MONITOR_ENABLED}
  replicaCount: ${SERVICE_DISPATCH_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-dispatch-monitor-${SERVICE_DISPATCH_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-dispatch-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_DISPATCH_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- service-outage-monitor-1 subchart specific configuration
service-outage-monitor-1:
  enabled: ${SERVICE_OUTAGE_MONITOR_1_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_1_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-outage-monitor-1-${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
    enable_triage_monitoring: "0"
    # -- Velocloud hosts
    velocloud_hosts: ${VELOCLOUD_HOST_1}
    # -- Filter for Velocloud hosts
    velocloud_hosts_filter: ${VELOCLOUD_HOST_1_FILTER}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- service-outage-monitor-2 subchart specific configuration
service-outage-monitor-2:
  enabled: ${SERVICE_OUTAGE_MONITOR_2_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_2_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-outage-monitor-2-${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
    enable_triage_monitoring: "0"
    # -- Velocloud hosts
    velocloud_hosts: ${VELOCLOUD_HOST_2}
    # -- Filter for Velocloud hosts
    velocloud_hosts_filter: ${VELOCLOUD_HOST_2_FILTER}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- service-outage-monitor-3 subchart specific configuration
service-outage-monitor-3:
  enabled: ${SERVICE_OUTAGE_MONITOR_3_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_3_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-outage-monitor-3-${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
    enable_triage_monitoring: "0"
    # -- Velocloud hosts
    velocloud_hosts: ${VELOCLOUD_HOST_3}
    # -- Filter for Velocloud hosts
    velocloud_hosts_filter: ${VELOCLOUD_HOST_3_FILTER}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- service-outage-monitor-4 subchart specific configuration
service-outage-monitor-4:
  enabled: ${SERVICE_OUTAGE_MONITOR_4_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_4_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-outage-monitor-4-${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
    enable_triage_monitoring: "0"
    # -- Velocloud hosts
    velocloud_hosts: ${VELOCLOUD_HOST_4}
    # -- Filter for Velocloud hosts
    velocloud_hosts_filter: ${VELOCLOUD_HOST_4_FILTER}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- service-outage-monitor-triage subchart specific configuration
service-outage-monitor-triage:
  enabled: ${SERVICE_OUTAGE_MONITOR_TRIAGE_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_TRIAGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-outage-monitor-triage-${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
    enable_triage_monitoring: "1"
    # -- Velocloud hosts
    velocloud_hosts: ${VELOCLOUD_HOST_TRIAGE}
    # -- Filter for Velocloud hosts
    velocloud_hosts_filter: ${VELOCLOUD_HOST_FILTER_TRIAGE}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- sites-monitor subchart specific configuration
sites-monitor:
  enabled: ${SITES_MONITOR_ENABLED}
  replicaCount: ${SITES_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "sites-monitor-${SITES_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    metrics:
      # -- Indicates whether the microservice will expose metrics through prometheus.
      enabled: true
      svc:
        port: 9090
        name: metrics
      ## Additional labels for the service monitor
      ## in case you use "serviceMonitorNamespaceSelector" in Prometheus CRD
      labels: {}
      #labels:
      #  servicediscovery: true
    # -- Period in second for do monitoring process
    monitoring_seconds: ${MONITORING_SECONDS}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/sites-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SITES_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- t7-bridge subchart specific configuration
t7-bridge:
  enabled: ${T7_BRIDGE_ENABLED}
  replicaCount: ${T7_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "t7-bridge-${T7_BRIDGE_BUILD_NUMBER}"
    # -- KRE Base URL to make calls for get tickets predictions
    kre_base_url: ${KRE_TNBA_BASE_URL}
    # -- Base URL for T7 API
    t7_base_url: ${T7_BASE_URL}
    ## -- Token credentials for T7 API
    t7_token: ${T7_TOKEN}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/t7-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${T7_BRIDGE_BUILD_NUMBER}
  imagePullSecrets: [ ]
  nameOverride: ""
  fullnameOverride: ""
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${T7_BRIDGE_ENABLED}
    minReplicas: ${T7_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- ticket-collector subchart specific configuration
ticket-collector:
  enabled: ${TICKET_COLLECTOR_ENABLED}
  replicaCount: ${TICKET_COLLECTOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "ticket-collector-${TICKET_COLLECTOR_BUILD_NUMBER}"
    # -- Indicate the interval task that must run in parallel
    interval_tasks_run: "1"
    # -- Indicate mongo username
    mongodb_username: ${TICKET_COLLECTOR_MONGO_USERNAME}
    # -- Indicate mongo password
    mongodb_password: ${TICKET_COLLECTOR_MONGO_PASSWORD}
    # -- Indicate mongo hostname
    mongodb_host: ${TICKET_COLLECTOR_MONGO_HOST}
    # -- Indicate mongo database to use
    mongodb_database: ${TICKET_COLLECTOR_MONGO_DB_NAME}
    # -- Client ID credentials for Bruin API
    bruin_client_id: ${BRUIN_CLIENT_ID}
    # -- Client Secret credentials for Bruin API
    bruin_client_secret: ${BRUIN_CLIENT_SECRET}
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/ticket-collector
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${TICKET_COLLECTOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- ticket-statistics subchart specific configuration
ticket-statistics:
  enabled: ${TICKET_STATISTICS_ENABLED}
  replicaCount: ${TICKET_STATISTICS_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "ticket-statistics-${TICKET_STATISTICS_BUILD_NUMBER}"
    # -- Indicate mongo username
    mongodb_username: ${TICKET_COLLECTOR_MONGO_USERNAME}
    # -- Indicate mongo password
    mongodb_password: ${TICKET_COLLECTOR_MONGO_PASSWORD}
    # -- Indicate mongo hostname
    mongodb_host: ${TICKET_COLLECTOR_MONGO_HOST}
    # -- Indicate mongo database to use
    mongodb_database: ${TICKET_COLLECTOR_MONGO_DB_NAME}
    # -- Indicate ticket statistics server port
    server_port: 5000
    # -- Indicate ticket statistics server root path
    server_root_path: "/api"
    # -- Indicate ticket statistics server version
    server_version: ${TICKET_STATISTICS_BUILD_NUMBER}
    # -- Indicate ticket statistics server name
    server_name: ticket-statistics
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/ticket-statistics
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${TICKET_STATISTICS_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- tnba-feedback subchart specific configuration
tnba-feedback:
  enabled: ${TNBA_FEEDBACK_ENABLED}
  replicaCount: ${TNBA_FEEDBACK_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "tnba-feedback-${TNBA_FEEDBACK_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/tnba-feedback
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${TNBA_FEEDBACK_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- tnba-monitor subchart specific configuration
tnba-monitor:
  enabled: ${TNBA_MONITOR_ENABLED}
  replicaCount: ${TNBA_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "tnba-monitor-${TNBA_MONITOR_BUILD_NUMBER}"
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/tnba-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${TNBA_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi


# -- velocloud-bridge subchart specific configuration
velocloud-bridge:
  enabled: ${VELOCLOUD_BRIDGE_ENABLED}
  replicaCount: ${VELOCLOUD_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "velocloud-bridge-${VELOCLOUD_BRIDGE_BUILD_NUMBER}"
    # -- Velocloud credentials
    velocloud_credentials: ${VELOCLOUD_CREDENTIALS}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/velocloud-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${VELOCLOUD_BRIDGE_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${VELOCLOUD_BRIDGE_ENABLED}
    minReplicas: ${VELOCLOUD_BRIDGE_DESIRED_TASKS}
    maxReplicas: 3
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80