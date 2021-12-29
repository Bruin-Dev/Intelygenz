# -- nats helm chart configuration
nats:
  cluster:
    enabled: true
  natsbox:
    enabled: false
  # -- override name to use nats as name for svc, deployment and all created by nats helm chart
  nameOverride: "nats"


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
    bruin_login_url_ip: ${BRUIN_BRIDGE__BRUIN_LOGIN_URL_IP}
    # -- IP of Bruin DEV Base URL
    bruin_base_url_ip: ${BRUIN_BRIDGE__BRUIN_BASE_URL_IP}
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
    digi_api_test_ip: ${DIGI_BRIDGE__DIGI_REBOOT_API_TEST_IP}
    # -- Record name for Digi Test Environment
    digi_api_test_dns_record_name: ${DIGI_BRIDGE__DIGI_REBOOT_API_TEST_DNS_RECORD_NAME}
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
    # -- Username to log into Dri API
    dri_acc_email: "${DRI_ACC_EMAIL}"
    # -- Password to log into Dri API
    dri_acc_password: "${DRI_ACC_PASSWORD}"
    # -- Base URL for Dri API
    dri_base_url: "${DRI_BASE_URL}"
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
    # -- Base URL for KRE API
    kre_base_url: ${KRE_REPAIR_TICKETS_BASE_URL}
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


# -- service-outage-monitor (SOM) subchart specific configuration
service-outage-monitor:
  enabled: ${SERVICE_OUTAGE_MONITOR_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_DESIRED_TASKS}
  config:
    # -- Indicate the capabilities dependencies
    <<: *capabilitiesEnabled
    # -- SOM Velocloud Hosts to monitor:
    som_monitored_velocloud_hosts: [${SOM_MONITORED_VELOCLOUD_HOSTS}]
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