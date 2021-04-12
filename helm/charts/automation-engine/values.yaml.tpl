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

# -- Global configuration for all subcharts
global:
  # -- Name of environment for EKS cluster and network resources
  current_environment: ${CURRENT_ENVIRONMENT}
  # -- Name of environment for helm charts and
  # redis elasticaches used
  environment: ${ENVIRONMENT_SLUG}
  # -- NATS cluster endpoint used by bruin-bridge
  nats_server: "nats://nats:4222"
  # -- Redis Hostname used to store heavy NATS messages (>1MB)
  redis_hostname: ${REDIS_HOSTNAME}
  # -- Redis Hostname used to store metrics obtained from tnba-feedback to train the ML model
  redis_tnba_feedback_hostname: ${REDIS_TNBA_FEEDBACK_HOSTNAME}
  # -- Redis hostname used to store information used by customer-cache
  redis_customer_cache_hostname: ${REDIS_CUSTOMER_CACHE_HOSTNAME}
  # -- Indicates if the logs will be sent to papertrail or not.
  papertrail_active: "False"
  # -- Papertrail host to which the logs will be sent
  papertrail_host: "logs.papertrailapp.com"
  # -- Papertrail port to which the logs will be sent
  papertrail_port: "0"
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

# -- customer-cache subchart specific configuration
customer-cache:
  enabled: ${CUSTOMER_CACHE_ENABLED}
  replicaCount: ${CUSTOMER_CACHE_DESIRED_TASKS}
  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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
  replicaCount: ${DIGI_BRIDGE_DESIRED_TASKS}

  # -- Field to indicate if the digi-bridge module is going to be deployed
  enabled: ${DIGI_BRIDGE_ENABLED}

  # digi-bridge specific configuration variables
  config:
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

dispatch-portal-backend:
  enabled: ${DISPATCH_PORTAL_BACKEND_ENABLED}
  replicaCount: ${DISPATCH_PORTAL_BACKEND_DESIRED_TASKS}
  config:
    dispatch_portal_server_port: 5000
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

# -- hawkeye-affecting-monitor subchart specific configuration
hawkeye-affecting-monitor:
  enabled: ${HAWKEYE_AFFECTING_MONITOR_ENABLED}
  replicaCount: ${HAWKEYE_AFFECTING_MONITOR_DESIRED_TASKS}

  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

  autoscaling:
    enabled: false
    minReplicas: 1
    maxReplicas: 100
    targetCPUUtilizationPercentage: 80
    # targetMemoryUtilizationPercentage: 80

  nodeSelector: {}

  tolerations: []

  affinity: {}

# -- hawkeye-bridge subchart specific configuration
hawkeye-bridge:
  replicaCount: ${HAWKEYE_BRIDGE_DESIRED_TASKS}

  enabled: ${HAWKEYE_BRIDGE_ENABLED}

  config:
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

# -- hawkeye-customer-cache specific configuration
hawkeye-customer-cache:
  enabled: ${HAWKEYE_CUSTOMER_CACHE_ENABLED}
  replicaCount: ${HAWKEYE_CUSTOMER_CACHE_DESIRED_TASKS}
  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

hawkeye-outage-monitor:
  enabled: ${HAWKEYE_OUTAGE_MONITOR_ENABLED}
  replicaCount: ${HAWKEYE_OUTAGE_MONITOR_DESIRED_TASKS}
  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

last-contact-report:
  enabled: ${LAST_CONTACT_REPORT_ENABLED}
  replicaCount: ${LAST_CONTACT_REPORT_DESIRED_TASKS}
  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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


# -- lit-bridge subchart specific configuration
lit-bridge:
  # -- Number of lit-bridge pods to do calls to LIT API.
  replicaCount: ${LIT_BRIDGE_DESIRED_TASKS}

  enabled: ${LIT_BRIDGE_ENABLED}

  config:
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

lumin-billing-report:
  enabled: ${LUMIN_BILLING_REPORT_ENABLED}
  replicaCount: ${LUMIN_BILLING_REPORT_DESIRED_TASKS}
  config:
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

  autoscaling:
    enabled: false
    minReplicas: 1
    maxReplicas: 100
    targetCPUUtilizationPercentage: 80

# -- notifier subchart specific configuration
notifier:
  replicaCount: ${NOTIFIER_DESIRED_TASKS}
  # -- Field to indicate if the notifier module is going to be deployed
  enabled: ${NOTIFIER_ENABLED}
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

service-affecting-monitor:
  enabled: ${SERVICE_AFFECTING_MONITOR_ENABLED}
  replicaCount: ${SERVICE_AFFECTING_MONITOR_DESIRED_TASKS}
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

service-dispatch-monitor:
  enabled: ${SERVICE_DISPATCH_MONITOR_ENABLED}
  replicaCount: ${SERVICE_DISPATCH_MONITOR_DESIRED_TASKS}
  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

service-outage-monitor-1:
  enabled: ${SERVICE_OUTAGE_MONITOR_1_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_1_DESIRED_TASKS}
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

service-outage-monitor-2:
  enabled: true
  replicaCount: 1
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

service-outage-monitor-3:
  enabled: true
  replicaCount: 1
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

service-outage-monitor-4:
  enabled: true
  replicaCount: 1
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

service-outage-monitor-triage:
  enabled: ${SERVICE_OUTAGE_MONITOR_TRIAGE_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_TRIAGE_DESIRED_TASKS}
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

sites-monitor:
  enabled: true
  replicaCount: 1
  config:
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
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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
  replicaCount: 1
  config:
    # -- KRE Base URL to make calls for get tickets predictions
    kre_base_url: ${KRE_BASE_URL}
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

tnba-feedback:
  enabled: ${TNBA_FEEDBACK_ENABLED}
  replicaCount: ${TNBA_FEEDBACK_DESIRED_TASKS}
  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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

tnba-monitor:
  enabled: ${TNBA_MONITOR_ENABLED}
  replicaCount: ${TNBA_MONITOR_DESIRED_TASKS}

  config:
    capabilities_enabled:
      # -- Indicate is bruin-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # bruin-bridge service responds correctly to healthcheck calls.
      bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
      # -- Indicate is cts-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # cts-bridge service responds correctly to healthcheck calls.
      cts_bridge: ${CTS_BRIDGE_ENABLED}
      # -- Indicate is hawkeye-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # hawkeye-bridge service responds correctly to healthcheck calls.
      hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
      # -- Indicate is lit-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # lit-bridge service responds correctly to healthcheck calls.
      lit_bridge: ${LIT_BRIDGE_ENABLED}
      # -- Indicate is notifier is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # notifier service responds correctly to healthcheck calls.
      notifier: ${NOTIFIER_ENABLED}
      # -- Indicate is t8-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # t7-bridge service responds correctly to healthcheck calls.
      t7_bridge: ${T7_BRIDGE_ENABLED}
      # -- Indicate is velocloud-bridge is going to be activated. If it is true an initContainer
      # will be created in the tnba-monitor deployment that will wait until the
      # velocloud-bridge service responds correctly to healthcheck calls.
      velocloud_bridge: ${VELOCLOUD_BRIDGE_ENABLED}

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
  replicaCount: 1

  enabled: true

  config:
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
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}
