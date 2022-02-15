# -- nats helm chart configuration
nats:
  enabled: ${NATS_SERVER_ENABLED}
  cluster:
    enabled: true
    replicas: ${NATS_SERVER_DESIRED_TASKS}
  natsbox:
    enabled: false
  # -- override name to use nats as name for svc, deployment and all created by nats helm chart
  nameOverride: "nats"


# -- prometheus-nats-exporter helm chart configuration to get Nats metrics in prometheus
prometheus-nats-exporter:
  # enable or disable prometheus-nats-exporter
  enabled: ${PROMETHEUS_NATS_EXPORTER_ENABLED}
  nameOverride: prometheus-nats-exporter-${ENVIRONMENT_NAME}
  fullnameOverride: prometheus-nats-exporter-${ENVIRONMENT_NAME}
  # if using the Prometheus Operator enable serviceMonitor
  serviceMonitor:
    enabled: ${PROMETHEUS_NATS_EXPORTER_ENABLED}
    additionalLabels: {}
    namespace: prometheus
    interval: "15s"
    scrapeTimeout: "10s"
  # set resources
  resources:
    limits:
      cpu: 100m
      memory: 128Mi
    requests:
      cpu: 100m
      memory: 128Mi
  config:
    # Nats data
    nats:
      # See https://github.com/helm/charts/blob/master/stable/nats/templates/monitoring-svc.yaml
      service: automation-engine-nats
      namespace: ${NAMESPACE}
      port: 8222
    metrics:
      channelz: false
      connz: false
      jsz: false
      gatewayz: false
      routez: false
      serverz: false
      subz: true
      varz: true


## YAML anchor to define capabilities_enabled
.capabilitiesEnabled: &capabilitiesEnabled
  capabilities_enabled:
    # -- Indicate if bruin-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # bruin-bridge service responds correctly to healthcheck calls.
    bruin_bridge: ${BRUIN_BRIDGE_ENABLED}
    # -- Indicate if customer-cache is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # customer-cache service responds correctly to healthcheck calls.
    customer_cache: ${CUSTOMER_CACHE_ENABLED}
    # -- Indicate if digi-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # digi-bridge service responds correctly to healthcheck calls.
    digi_bridge: ${DIGI_BRIDGE_ENABLED}
    # -- Indicate if email-tagger-kre-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # email-tagger-kre-bridge service responds correctly to healthcheck calls.
    email_tagger_kre_bridge: ${EMAIL_TAGGER_KRE_BRIDGE_ENABLED}
    # -- Indicate if repair-tickets-kre-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # repair-tickets-kre-bridge service responds correctly to healthcheck calls.
    repair_tickets_kre_bridge: ${REPAIR_TICKETS_KRE_BRIDGE_ENABLED}
    # -- Indicate if hawkeye-bridge is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # hawkeye-bridge service responds correctly to healthcheck calls.
    hawkeye_bridge: ${HAWKEYE_BRIDGE_ENABLED}
    # -- Indicate if hawkeye-customer-cache is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # hawkeye-customer-cache service responds correctly to healthcheck calls.
    hawkeye_customer_cache: ${HAWKEYE_CUSTOMER_CACHE_ENABLED}
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
  nats_server: "nats://automation-engine-nats:4222"
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
  # -- Timezone used for periodic jobs, timestamps...
  timezone: ${TIMEZONE}
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
    bruin_client_id: ${BRUIN_BRIDGE__BRUIN_CLIENT_ID}
    # -- Client Secret credentials for Bruin API
    bruin_client_secret: ${BRUIN_BRIDGE__BRUIN_CLIENT_SECRET}
    # -- Login URL for Bruin API
    bruin_login_url: ${BRUIN_BRIDGE__BRUIN_LOGIN_URL}
    # -- Base URL for Bruin API
    bruin_base_url: ${BRUIN_BRIDGE__BRUIN_BASE_URL}
    # -- IP of Bruin DEV Login URL
    bruin_login_url_ip: "${BRUIN_BRIDGE__BRUIN_LOGIN_URL_IP}"
    # -- IP of Bruin DEV Base URL
    bruin_base_url_ip: "${BRUIN_BRIDGE__BRUIN_BASE_URL_IP}"
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
  resources:
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
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "customer-cache-${CUSTOMER_CACHE_BUILD_NUMBER}"
    # -- VeloCloud hosts whose edges will be stored to the cache
    velocloud_hosts: ${CUSTOMER_CACHE__VELOCLOUD_HOSTS}
    # -- E-mail address that will get e-mails with a relation of service numbers that have multiple Bruin inventories
    duplicate_inventories_recipient: ${CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}
    # -- Defines how often the cache is refreshed
    refresh_job_interval: ${CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}
    # -- Defines how often the next refresh flag is checked to decide if it's time to refresh the cache or not
    refresh_check_interval: ${CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL}
    # -- VeloCloud edges that should be ignored in the caching process
    blacklisted_edges: ${CUSTOMER_CACHE__BLACKLISTED_EDGES}
    # -- Client IDs whose edges have Pending management status that should be ignored in the caching process
    blacklisted_clients_with_pending_status: ${CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS}
    # -- Management statuses that should be considered in the caching process
    whitelisted_management_statuses: ${CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}
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
    digi_client_id: ${DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_ID}
    # -- Client Secret credentials for Digi API
    digi_client_secret: ${DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_SECRET}
    # -- Base URL for Digi API
    digi_base_url: ${DIGI_BRIDGE__DIGI_REBOOT_API_BASE_URL}
    # -- Auth tokens TTL
    digi_token_ttl: ${DIGI_BRIDGE__DIGI_REBOOT_API_TOKEN_TTL}
    # -- IP for Digi Environment
    digi_api_ip: ${DIGI_BRIDGE__DIGI_REBOOT_API_IP}
    # -- Record name for Digi Production Environment
    digi_api_dns_record_name: ${DIGI_BRIDGE__DIGI_REBOOT_API_DNS_RECORD_NAME}
    # -- IP for Digi Test Environment
    digi_api_test_ip: "${DIGI_BRIDGE__DIGI_REBOOT_API_TEST_IP}"
    # -- Record name for Digi Test Environment
    digi_api_test_dns_record_name: "${DIGI_BRIDGE__DIGI_REBOOT_API_TEST_DNS_RECORD_NAME}"
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
    # -- Defines how often the report is built and sent
    job_interval: ${DIGI_REBOOT_REPORT__REPORT_JOB_INTERVAL}
    # -- Defines how much time back to look for DiGi Reboot logs
    logs_lookup_interval: ${DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL}
    # -- Email address to send the report
    recipient: ${DIGI_REBOOT_REPORT__REPORT_RECIPIENT}
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
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


# -- dri-bridge subchart specific configuration
dri-bridge:
  # -- Field to indicate if the dri-bridge module is going to be deployed
  enabled: ${DRI_BRIDGE_ENABLED}
  replicaCount: ${DRI_BRIDGE_DESIRED_TASKS}
  # dri-bridge specific configuration variables
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "dri-bridge-${DRI_BRIDGE_BUILD_NUMBER}"
    # -- Username to log into DRI API
    username: ${DRI_BRIDGE__USERNAME}
    # -- Password to log into DRI API
    password: ${DRI_BRIDGE__PASSWORD}
    # -- Base URL for DRI API
    base_url: ${DRI_BRIDGE__BASE_URL}
    # -- Defines how much time the data retrieved from DRI for a specific device can be stored and served from Redis
    dri_data_redis_ttl: ${DRI_BRIDGE__DRI_DATA_REDIS_TTL}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/dri-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${DRI_BRIDGE_BUILD_NUMBER}
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
    enabled: ${DRI_BRIDGE_ENABLED}
    minReplicas: ${DRI_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- email-tagger-kre-bridge subchart specific configuration
email-tagger-kre-bridge:
  enabled: ${EMAIL_TAGGER_KRE_BRIDGE_ENABLED}
  replicaCount: ${EMAIL_TAGGER_KRE_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "email-tagger-kre-bridge-${EMAIL_TAGGER_KRE_BRIDGE_BUILD_NUMBER}"
    # -- Base URL for E-mail Tagger's KRE
    kre_base_url: ${EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL}
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
    # -- Defines how often new emails received from Bruin are processed
    new_emails_job_interval: ${EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL}
    # -- Defines how often new tickets received from Bruin are sent to the KRE to train the AI model
    new_tickets_job_interval: ${EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL}
    # -- Defines how many simultaneous emails are processed
    max_concurrent_emails: ${EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS}
    # -- Defines how many simultaneous tickets are sent to the KRE to train the AI model
    max_concurrent_tickets: ${EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS}
    # -- API request key for incoming requests
    api_request_key: ${EMAIL_TAGGER_MONITOR__API_REQUEST_KEY}
    # -- API signature secret key for incoming requests
    api_request_signature_secret_key: ${EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY}
    # -- API server endpoint prefix for incoming requests
    api_endpoint_prefix: ${EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX}
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
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


# -- fraud-monitor subchart specific configuration
fraud-monitor:
  enabled: ${FRAUD_MONITOR_ENABLED}
  replicaCount: ${FRAUD_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "fraud-monitor-${FRAUD_MONITOR_BUILD_NUMBER}"
    # -- Defines how often Fraud e-mails are checked to report them as Service Affecting tickets
    monitoring_job_interval: ${FRAUD_MONITOR__MONITORING_JOB_INTERVAL}
    # -- E-mail account that receives Fraud e-mails for later analysis
    observed_inbox_email_address: ${FRAUD_MONITOR__OBSERVED_INBOX_EMAIL_ADDRESS}
    # -- Senders addresses whose e-mail messages represent Fraud alerts
    observed_inbox_senders: ${FRAUD_MONITOR__OBSERVED_INBOX_SENDERS}
    # -- Default contact details used when a Fraud is reported as a Service Affecting ticket
    default_contact_for_new_tickets: ${FRAUD_MONITOR__DEFAULT_CONTACT_FOR_NEW_TICKETS}
    # -- Default client info used when the DID device in the Fraud alert does not have an inventory assigned in Bruin
    default_client_info_for_did_without_inventory: ${FRAUD_MONITOR__DEFAULT_CLIENT_INFO_FOR_DID_WITHOUT_INVENTORY}
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/fraud-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${FRAUD_MONITOR_BUILD_NUMBER}
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
    # -- Defines how often devices are checked to find and report issues
    monitoring_job_interval: ${HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL}
    # -- Defines how much time back to look for probes' tests results
    probes_tests_results_lookup_interval: ${HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL}
    # -- Bruin's product category under monitoring
    monitored_product_category: ${HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY}
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
    # -- Client username to log into Hawkeye API
    client_username: ${HAWKEYE_BRIDGE__CLIENT_USERNAME}
    # -- Client password to log into Hawkeye API
    client_password: ${HAWKEYE_BRIDGE__CLIENT_PASSWORD}
    # -- Base URL to access Hawkeye API
    base_url: ${HAWKEYE_BRIDGE__BASE_URL}
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
    # -- E-mail address that will get e-mails with a relation of service numbers that have multiple Bruin inventories
    duplicate_inventories_recipient: ${CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}
    # -- Defines how often the cache is refreshed
    refresh_job_interval: ${CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}
    # -- Management statuses that should be considered in the caching process
    whitelisted_management_statuses: ${CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}
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
    # -- Defines how often devices are checked to find and report issues
    monitoring_job_interval: ${HAWKEYE_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL}
    # -- Defines how much time to wait before checking if a particular device is still in outage state
    quarantine_for_devices_in_outage: ${HAWKEYE_OUTAGE_MONITOR__QUARANTINE_FOR_DEVICES_IN_OUTAGE}
    # -- Bruin's product category under monitoring
    monitored_product_category: ${HAWKEYE_OUTAGE_MONITOR__MONITORED_PRODUCT_CATEGORY}
    # -- Defines for how long a ticket can be auto-resolved after the last documented outage
    grace_period_to_autoresolve_after_last_documented_outage: ${HAWKEYE_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE}
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
    # -- Defines how often InterMapper events are checked to find and report issues
    monitoring_job_interval: ${INTERMAPPER_OUTAGE_MONITOR__MONITORING_JOB_INTERVAL}
    # -- E-mail account that receives InterMapper events for later analysis
    observed_inbox_email_address: ${INTERMAPPER_OUTAGE_MONITOR__OBSERVED_INBOX_EMAIL_ADDRESS}
    # -- Senders addresses whose e-mail messages represent InterMapper events
    observed_inbox_senders: ${INTERMAPPER_OUTAGE_MONITOR__OBSERVED_INBOX_SENDERS}
    # -- InterMapper events considered as DOWN
    monitored_down_events: ${INTERMAPPER_OUTAGE_MONITOR__MONITORED_DOWN_EVENTS}
    # -- InterMapper events considered as UP
    monitored_up_events: ${INTERMAPPER_OUTAGE_MONITOR__MONITORED_UP_EVENTS}
    # -- Defines how many simultaneous email batches related to the same InterMapper asset are processed
    max_concurrent_email_batches: ${INTERMAPPER_OUTAGE_MONITOR__MAX_CONCURRENT_EMAIL_BATCHES}
    # -- Defines which Bruin product categories are taken into account when auto-resolving tickets
    whitelisted_product_categories_for_autoresolve: ${INTERMAPPER_OUTAGE_MONITOR__WHITELISTED_PRODUCT_CATEGORIES_FOR_AUTORESOLVE}
    # -- Defines for how long a ticket can be auto-resolved after the last documented outage
    grace_period_to_autoresolve_after_last_documented_outage: ${INTERMAPPER_OUTAGE_MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE}
    # -- Parameters to fetch from DRI to include them in InterMapper notes for PIAB devices
    dri_parameters_for_piab_notes: ${INTERMAPPER_OUTAGE_MONITOR__DRI_PARAMETERS_FOR_PIAB_NOTES}
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
    # -- VeloCloud hosts whose edges will be used to build the report
    monitored_velocloud_hosts: ${LAST_CONTACT_REPORT__MONITORED_VELOCLOUD_HOSTS}
    # -- Email address to send the report
    recipient: ${LAST_CONTACT_REPORT__REPORT_RECIPIENT}
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
    # -- Slack webhook to send messages
    slack_webhook: ${NOTIFIER__SLACK_WEBHOOK_URL}
    # -- Email account used to send messages to other accounts (username)
    email_account_for_message_delivery_username: ${NOTIFIER__EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_USERNAME}
    # -- Email account used to send messages to other accounts (password)
    email_account_for_message_delivery_password: ${NOTIFIER__EMAIL_ACCOUNT_FOR_MESSAGE_DELIVERY_PASSWORD}
    # -- Mapping of e-mail addresses and passwords whose inboxes can be read for later analysis
    monitorable_email_accounts: ${NOTIFIER__MONITORABLE_EMAIL_ACCOUNTS}
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


# -- repair-tickets-kre-bridge subchart specific configuration
repair-tickets-kre-bridge:
  enabled: ${REPAIR_TICKETS_KRE_BRIDGE_ENABLED}
  replicaCount: ${REPAIR_TICKETS_KRE_BRIDGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "repair-tickets-kre-bridge-${REPAIR_TICKETS_KRE_BRIDGE_BUILD_NUMBER}"
    # -- Base URL for RTA's KRE
    kre_base_url: ${REPAIR_TICKETS_KRE_BRIDGE__KRE_BASE_URL}
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/repair-tickets-kre-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${REPAIR_TICKETS_KRE_BRIDGE_BUILD_NUMBER}
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
    enabled: ${REPAIR_TICKETS_KRE_BRIDGE_ENABLED}
    minReplicas: ${REPAIR_TICKETS_KRE_BRIDGE_DESIRED_TASKS}
    maxReplicas: 2
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- repair-tickets-monitor subchart specific configuration
repair-tickets-monitor:
  enabled: ${REPAIR_TICKETS_MONITOR_ENABLED}
  replicaCount: ${REPAIR_TICKETS_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "repair-tickets-monitor-${REPAIR_TICKETS_MONITOR_BUILD_NUMBER}"
    # -- Defines how often new emails tagged by the E-mail Tagger are processed
    rta_monitor_job_interval: ${REPAIR_TICKETS_MONITOR__RTA_MONITOR_JOB_INTERVAL}
    # -- Defines how often new created tickets fetched from Bruin are sent to the KRE to train the AI model
    new_created_tickets_feedback_job_interval: ${REPAIR_TICKETS_MONITOR__NEW_CREATED_TICKETS_FEEDBACK_JOB_INTERVAL}
    # -- Defines how often new closed tickets fetched from Bruin are sent to the KRE to train the AI model
    new_closed_tickets_feedback_job_interval: ${REPAIR_TICKETS_MONITOR__NEW_CLOSED_TICKETS_FEEDBACK_JOB_INTERVAL}
    # -- Defines how many simultaneous tagged emails are processed
    max_concurrent_emails_for_monitoring: ${REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_EMAILS_FOR_MONITORING}
    # -- Defines how many simultaneous new created tickets are sent to the KRE to train the AI model
    max_concurrent_created_tickets_for_feedback: ${REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_CREATED_TICKETS_FOR_FEEDBACK}
    # -- Defines how many simultaneous new closed tickets are sent to the KRE to train the AI model
    max_concurrent_closed_tickets_for_feedback: ${REPAIR_TICKETS_MONITOR__MAX_CONCURRENT_CLOSED_TICKETS_FOR_FEEDBACK}
    # -- Mapping of tag names and their corresponding numeric ID, as defined in the AI model
    tag_ids_mapping: ${REPAIR_TICKETS_MONITOR__TAG_IDS_MAPPING}
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
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/repair-tickets-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${REPAIR_TICKETS_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 300m
      memory: 384Mi
    requests:
      cpu: 150m
      memory: 192Mi


# -- service-affecting-monitor subchart specific configuration
service-affecting-monitor:
  enabled: ${SERVICE_AFFECTING_MONITOR_ENABLED}
  replicaCount: ${SERVICE_AFFECTING_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-affecting-monitor-${SERVICE_AFFECTING_MONITOR_BUILD_NUMBER}"
    # -- Indicates if the monitor reports process will be executed on start or not
    exec_monitor_reports_on_start: ${EXEC_MONITOR_REPORTS_ON_START}
    # -- Indicates if the bandwidth reports process will be executed on start or not
    exec_bandwidth_reports_on_start: ${EXEC_BANDWIDTH_REPORTS_ON_START}
    # -- Bruin's product category under monitoring
    monitored_product_category: ${SERVICE_AFFECTING__MONITORED_PRODUCT_CATEGORY}
    # -- [Monitoring] Defines how often devices are checked to find and report issues
    monitoring__monitoring_job_interval: ${SERVICE_AFFECTING__MONITOR__MONITORING_JOB_INTERVAL}
    # -- [Monitoring] VeloCloud hosts whose edges will be monitored
    monitoring__monitored_velocloud_hosts: ${SERVICE_AFFECTING__MONITOR__MONITORED_VELOCLOUD_HOSTS}
    # -- [Monitoring] Mapping of VeloCloud hosts, Bruin customers and default contact info
    monitoring__default_contact_info_per_customer: ${SERVICE_AFFECTING__MONITOR__DEFAULT_CONTACT_INFO_PER_CUSTOMER}
    # -- [Monitoring] List Bruin customers that should always use the default contact info
    monitoring__customers_to_always_use_default_contact_info: ${SERVICE_AFFECTING__MONITOR__CUSTOMERS_TO_ALWAYS_USE_DEFAULT_CONTACT_INFO}
    # -- [Monitoring] Threshold for Latency troubles
    monitoring__latency_monitoring_threshold: ${DEV__SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Packet Loss troubles
    monitoring__packet_loss_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Jitter troubles
    monitoring__jitter_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Bandwidth Over Utilization troubles
    monitoring__bandwidth_over_utilization_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Circuit Instability troubles
    monitoring__circuit_instability_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_THRESHOLD}
    # -- [Monitoring] Max DOWN events allowed in Circuit Instability checks while auto-resolving tickets
    monitoring__circuit_instability_autoresolve_threshold: ${DEV__SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD}
    # -- [Monitoring] Defines how much time back to look for Latency metrics in Latency checks
    monitoring__latency_monitoring_lookup_interval: ${SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_LOOKUP_INTERVAL}
    # -- [Monitoring] Defines how much time back to look for Packet Loss metrics in Packet Loss checks
    monitoring__packet_loss_monitoring_lookup_interval: ${SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_LOOKUP_INTERVAL}
    # -- [Monitoring] Defines how much time back to look for Jitter metrics in Jitter checks
    monitoring__jitter_monitoring_lookup_interval: ${SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_LOOKUP_INTERVAL}
    # -- [Monitoring] Defines how much time back to look for Bandwidth metrics in Bandwidth Over Utilization checks
    monitoring__bandwidth_over_utilization_monitoring_lookup_interval: ${SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_LOOKUP_INTERVAL}
    # -- [Monitoring] Defines how much time back to look for DOWN events in Circuit Instability checks
    monitoring__circuit_instability_monitoring_lookup_interval: ${SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL}
    # -- [Monitoring] Defines how much time back to look for all kinds of metrics while running auto-resolves
    monitoring__autoresolve_lookup_interval: ${SERVICE_AFFECTING__MONITOR__AUTORESOLVE_LOOKUP_INTERVAL}
    # -- [Monitoring] Defines for how long a ticket can be auto-resolved after the last documented trouble
    monitoring__grace_period_to_autoresolve_after_last_documented_trouble: ${SERVICE_AFFECTING__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_TROUBLE}
    # -- [Monitoring] Defines how many times a ticket can be auto-resolved
    monitoring__max_autoresolves_per_ticket: ${SERVICE_AFFECTING__MONITOR__MAX_AUTORESOLVES_PER_TICKET}
    # -- [Monitoring] List of client IDs for which Bandwidth Over Utilization checks are enabled
    monitoring__customers_with_bandwidth_over_utilization_monitoring: ${SERVICE_AFFECTING__MONITOR__CUSTOMERS_WITH_BANDWIDTH_OVER_UTILIZATION_MONITORING}
    # -- [Monitoring] List of link labels that are excluded from forwards to the ASR queue
    monitoring__link_labels_blacklisted_in_asr_forwards: ${SERVICE_AFFECTING__MONITOR__LINK_LABELS_BLACKLISTED_IN_ASR_FORWARDS}
    # -- [Reoccurring Trouble Report] Cron expression that determines when to build and deliver this report
    reoccurring_trouble_report__execution_cron_expression: ${SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__EXECUTION_CRON_EXPRESSION}
    # -- [Reoccurring Trouble Report] Troubles that will be reported
    reoccurring_trouble_report__reported_troubles: ${SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__REPORTED_TROUBLES}
    # -- [Reoccurring Trouble Report] Defines how much time back to look for Bruin tickets
    reoccurring_trouble_report__tickets_lookup_interval: ${SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__TICKETS_LOOKUP_INTERVAL}
    # -- [Reoccurring Trouble Report] Number of different tickets a trouble must appear in for a particular edge and interface to include it in the report
    reoccurring_trouble_report__reoccurring_trouble_tickets_threshold: ${SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__REOCCURRING_TROUBLE_TICKETS_THRESHOLD}
    # -- [Reoccurring Trouble Report] Mapping of Bruin customer IDs and recipients of these reports
    reoccurring_trouble_report__recipients_per_customer: ${SERVICE_AFFECTING__REOCCURRING_TROUBLE_REPORT__RECIPIENTS_PER_CUSTOMER}
    # -- [Daily Bandwidth Report] Cron expression that determines when to build and deliver this report
    daily_bandwidth_report__execution_cron_expression: ${SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__EXECUTION_CRON_EXPRESSION}
    # -- [Daily Bandwidth Report] Defines how much time back to look for bandwidth metrics and Bruin tickets
    daily_bandwidth_report__lookup_interval: ${SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__LOOKUP_INTERVAL}
    # -- [Daily Bandwidth Report] Customers for whom this report will be built
    daily_bandwidth_report__enabled_customers: ${SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__ENABLED_CUSTOMERS}
    # -- [Daily Bandwidth Report] List of recipients that will get these reports
    daily_bandwidth_report__recipients: ${SERVICE_AFFECTING__DAILY_BANDWIDTH_REPORT__RECIPIENTS}
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
      cpu: 300m
      memory: 384Mi
    requests:
      cpu: 150m
      memory: 192Mi


# -- service-outage-monitor subchart specific configuration
service-outage-monitor:
  enabled: ${SERVICE_OUTAGE_MONITOR_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_DESIRED_TASKS}
  config:
    # -- Bruin's product category under monitoring
    monitored_product_category: ${SERVICE_OUTAGE__MONITORED_PRODUCT_CATEGORY}
    # -- [Monitoring] Defines how often devices are checked to find and report issues
    monitoring__monitoring_job_interval: ${SERVICE_OUTAGE__MONITOR__MONITORING_JOB_INTERVAL}
    # -- [Monitoring] VeloCloud hosts whose edges will be monitored
    monitoring__monitored_velocloud_hosts: ${SERVICE_OUTAGE__MONITOR__MONITORED_VELOCLOUD_HOSTS}
    # -- [Monitoring] Defines how much time to wait before re-checking an edge currently in Link Down state
    monitoring__quarantine_for_edges_in_link_down_outage: ${SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_LINK_DOWN_OUTAGE}
    # -- [Monitoring] Defines how much time to wait before re-checking an edge currently in Hard Down state
    monitoring__quarantine_for_edges_in_hard_down_outage: ${SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HARD_DOWN_OUTAGE}
    # -- [Monitoring] Defines how much time to wait before re-checking an edge currently in Link Down (HA) state
    monitoring__quarantine_for_edges_in_ha_link_down_outage: ${SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_LINK_DOWN_OUTAGE}
    # -- [Monitoring] Defines how much time to wait before re-checking an edge currently in Soft Down (HA) state
    monitoring__quarantine_for_edges_in_ha_soft_down_outage: ${SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_SOFT_DOWN_OUTAGE}
    # -- [Monitoring] Defines how much time to wait before re-checking an edge currently in Hard Down (HA) state
    monitoring__quarantine_for_edges_in_ha_hard_down_outage: ${SERVICE_OUTAGE__MONITOR__QUARANTINE_FOR_EDGES_IN_HA_HARD_DOWN_OUTAGE}
    # -- [Monitoring] E-mail address that will receive a tiny report showing which edges from VeloCloud responses are not in the cache of customers
    monitoring__missing_edges_from_cache_report_recipient: ${SERVICE_OUTAGE__MONITOR__MISSING_EDGES_FROM_CACHE_REPORT_RECIPIENT}
    # -- [Monitoring] List of link labels that are excluded from forwards to the ASR queue
    monitoring__link_labels_blacklisted_in_asr_forwards: ${SERVICE_OUTAGE__MONITOR__LINK_LABELS_BLACKLISTED_IN_ASR_FORWARDS}
    # -- [Monitoring] List of edges that are excluded from Service Outage monitoring
    monitoring__blacklisted_edges: ${SERVICE_OUTAGE__MONITOR__BLACKLISTED_EDGES}
    # -- [Monitoring] Defines for how long a ticket can be auto-resolved after the last documented outage
    monitoring__grace_period_to_autoresolve_after_last_documented_outage: ${SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_TO_AUTORESOLVE_AFTER_LAST_DOCUMENTED_OUTAGE}
    # -- [Monitoring] Defines for how long the monitor will wait before attempting a new DiGi Reboot on an edge
    monitoring__grace_period_before_attempting_new_digi_reboots: ${SERVICE_OUTAGE__MONITOR__GRACE_PERIOD_BEFORE_ATTEMPTING_NEW_DIGI_REBOOTS}
    # -- [Monitoring] Severity level for Edge Down outages
    monitoring__severity_level_for_edge_down_outages: ${SERVICE_OUTAGE__MONITOR__SEVERITY_FOR_EDGE_DOWN_OUTAGES}
    # -- [Monitoring] Severity level for Link Down outages
    monitoring__severity_level_for_link_down_outages: ${SERVICE_OUTAGE__MONITOR__SEVERITY_FOR_LINK_DOWN_OUTAGES}
    # -- [Monitoring] Defines how many times a ticket can be auto-resolved
    monitoring__max_autoresolves_per_ticket: ${SERVICE_OUTAGE__MONITOR__MAX_AUTORESOLVES_PER_TICKET}
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
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 300m
      memory: 384Mi
    requests:
      cpu: 150m
      memory: 192Mi


# -- service-outage-monitor-triage subchart specific configuration
service-outage-monitor-triage:
  enabled: ${SERVICE_OUTAGE_MONITOR_TRIAGE_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_TRIAGE_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "service-outage-monitor-triage-${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
    # -- Bruin's product category under monitoring
    monitored_product_category: ${SERVICE_OUTAGE__MONITORED_PRODUCT_CATEGORY}
    # -- [Triage] Defines how often tickets are checked to see if it needs an initial triage or events note
    triage__monitoring_job_interval: ${SERVICE_OUTAGE__TRIAGE__MONITORING_JOB_INTERVAL}
    # -- [Triage] VeloCloud hosts whose edges will be monitored
    triage__monitored_velocloud_hosts: ${SERVICE_OUTAGE__TRIAGE__MONITORED_VELOCLOUD_HOSTS}
    # -- [Triage] Defines how many events will be included in events notes
    triage__max_events_per_event_note: ${SERVICE_OUTAGE__TRIAGE__MAX_EVENTS_PER_EVENT_NOTE}
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
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/service-outage-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}
  service:
    type: ClusterIP
    port: 5000
  resources:
    limits:
      cpu: 300m
      memory: 384Mi
    requests:
      cpu: 150m
      memory: 192Mi


# -- sites-monitor subchart specific configuration
sites-monitor:
  enabled: ${SITES_MONITOR_ENABLED}
  replicaCount: ${SITES_MONITOR_DESIRED_TASKS}
  config:
    # -- Papertrail prefix for create logs definition
    papertrail_prefix: "sites-monitor-${SITES_MONITOR_BUILD_NUMBER}"
    # -- Defines how often to look for links and edges, and write their data to the metrics server
    monitoring_job_interval: ${SITES_MONITOR__MONITORING_JOB_INTERVAL}
    # -- VeloCloud hosts whose edges will be monitored
    monitored_velocloud_hosts: ${SITES_MONITOR__MONITORED_VELOCLOUD_HOSTS}
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
    # -- Base URL for TNBA's KRE
    kre_base_url: ${T7_BRIDGE__KRE_BASE_URL}
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
    bruin_client_id: ${BRUIN_BRIDGE__BRUIN_CLIENT_ID}
    # -- Client Secret credentials for Bruin API
    bruin_client_secret: ${BRUIN_BRIDGE__BRUIN_CLIENT_SECRET}
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
      cpu: 300m
      memory: 1024Mi
    requests:
      cpu: 150m
      memory: 512Mi


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
      cpu: 300m
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
    # -- Bruin's product category under monitoring
    monitored_product_category: ${TNBA_FEEDBACK__MONITORED_PRODUCT_CATEGORY}
    # -- Defines how often tickets are pulled from Bruin and sent to the KRE to train the predictive model
    feedback_job_interval: ${TNBA_FEEDBACK__FEEDBACK_JOB_INTERVAL}
    # -- VeloCloud hosts whose edges will be monitored
    monitored_velocloud_hosts: ${TNBA_FEEDBACK__MONITORED_VELOCLOUD_HOSTS}
    # -- Defines for how long a ticket needs to wait before being re-sent to the KRE
    grace_period_before_resending_tickets: ${TNBA_FEEDBACK__GRACE_PERIOD_BEFORE_RESENDING_TICKETS}
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
    # -- Bruin's product category under monitoring
    monitored_product_category: ${TNBA_MONITOR__MONITORED_PRODUCT_CATEGORY}
    # -- Defines how often tickets are checked to see if they need a new TNBA note
    monitoring_job_interval: ${TNBA_MONITOR__MONITORING_JOB_INTERVAL}
    # -- VeloCloud hosts whose edges will be monitored
    monitored_velocloud_hosts: ${TNBA_MONITOR__MONITORED_VELOCLOUD_HOSTS}
    # -- List of edges that are excluded from TNBA monitoring
    blacklisted_edges: ${TNBA_MONITOR__BLACKLISTED_EDGES}
    # -- Defines for how long a ticket needs to wait since it was opened before appending a new TNBA note
    grace_period_before_appending_new_tnba_notes: ${TNBA_MONITOR__GRACE_PERIOD_BEFORE_APPENDING_NEW_TNBA_NOTES}
    # -- Defines for how long a Service Outage ticket needs to wait after the last documented outage to get a new TNBA note appended
    grace_period_before_monitoring_tickets_based_on_last_documented_outage: ${TNBA_MONITOR__GRACE_PERIOD_BEFORE_MONITORING_TICKETS_BASED_ON_LAST_DOCUMENTED_OUTAGE}
    # -- Defines the minimum confidence level required to consider a Request Completed / Repair Completed prediction accurate in TNBA auto-resolves
    min_required_confidence_for_request_and_repair_completed_predictions: ${TNBA_MONITOR__MIN_REQUIRED_CONFIDENCE_FOR_REQUEST_AND_REPAIR_COMPLETED_PREDICTIONS}
    # -- [Monitoring] Defines how much time back to look for DOWN events in Circuit Instability checks
    monitoring__circuit_instability_monitoring_lookup_interval: ${SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_MONITORING_LOOKUP_INTERVAL}
    # -- [Monitoring] Threshold for Latency troubles
    monitoring__latency_monitoring_threshold: ${DEV__SERVICE_AFFECTING__MONITOR__LATENCY_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Packet Loss troubles
    monitoring__packet_loss_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__PACKET_LOSS_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Jitter troubles
    monitoring__jitter_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__JITTER_MONITORING_THRESHOLD}
    # -- [Monitoring] Threshold for Bandwidth Over Utilization troubles
    monitoring__bandwidth_over_utilization_monitoring_threshold: ${SERVICE_AFFECTING__MONITOR__BANDWIDTH_OVER_UTILIZATION_MONITORING_THRESHOLD}
    # -- [Monitoring] Max DOWN events allowed in Circuit Instability checks while auto-resolving tickets
    monitoring__circuit_instability_autoresolve_threshold: ${DEV__SERVICE_AFFECTING__MONITOR__CIRCUIT_INSTABILITY_AUTORESOLVE_THRESHOLD}
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
    velocloud_credentials: ${VELOCLOUD_BRIDGE__VELOCLOUD_CREDENTIALS}
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