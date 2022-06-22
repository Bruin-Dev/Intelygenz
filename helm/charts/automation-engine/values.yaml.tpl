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
    # -- Indicate if velocloud-gateway-monitor is going to be activated. If it is true an initContainer
    # will be created in the microservice deployment that will wait until the
    # velocloud-gateway-monitor service responds correctly to healthcheck calls.
    velocloud_gateway_monitor: ${VELOCLOUD_GATEWAY_MONITOR_ENABLED}


# -- Global configuration for all subcharts
global:
  # -- Name of environment for EKS cluster and network resources
  current_environment: ${CURRENT_ENVIRONMENT}
  # -- Name of environment for helm charts
  environment: "${ENVIRONMENT_SLUG}"
  # -- Redis Hostname used to store heavy NATS messages (>1MB)
  redis_hostname: "ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/redis/main-hostname"
  # -- Redis Hostname used to store information used by customer-cache
  redis_customer_cache_hostname: "ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/redis/customer-cache-hostname"
  # -- Redis Hostname used to store metrics obtained from tnba-feedback to train the ML model
  redis_tnba_feedback_hostname: "ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/redis/tnba-feedback-hostname"
  # -- Redis Hostname used to store information used by email-tagger
  redis_email_tagger_hostname: "ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/redis/email-tagger-hostname"
  # -- external-secrets feature to sync parameters from AWS
  externalSecrets:
    # -- Enable/disable external-secrets
    enabled: true
    # -- Environment path to reference parameter store secrets
    envPath: "/automation-engine/${CURRENT_ENVIRONMENT_SHORT}"
    # -- Common path to reference parameter store secrets
    commonPath: "/automation-engine/common"
    # -- secretStorage configuration for create additional k8s resources to allow sync parameters from aws
    secretStorage:
      # -- Custom serviceAccount to assign AWS permissions
      serviceAccount:
        # -- AWS IAM role that have access to get parameters from AWS 
        # (needs secret-manager and ssm IAM permission, if use encryption also kms permissions)
        roleARN: "ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/external-secrets/iam-role-arn"
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
  config:
    # -- IP for Digi Environment
    digi_api_ip: ${DIGI_BRIDGE__DIGI_REBOOT_API_IP}
    # -- Record name for Digi Production Environment
    digi_api_dns_record_name: ${DIGI_BRIDGE__DIGI_REBOOT_API_DNS_RECORD_NAME}
    # -- IP for Digi Test Environment
    digi_api_test_ip: "${DIGI_BRIDGE__DIGI_REBOOT_API_TEST_IP}"
    # -- Record name for Digi Test Environment
    digi_api_test_dns_record_name: "${DIGI_BRIDGE__DIGI_REBOOT_API_TEST_DNS_RECORD_NAME}"
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
    # -- NATS cluster endpoint
    nats_server: "nats://automation-engine-nats:4222"
    # -- Redis Hostname used to store heavy NATS messages (>1MB)
    redis_hostname: ${REDIS_HOSTNAME}
    # -- Indicates if the logs will be sent to papertrail or not.
    papertrail_active: ${PAPERTRAIL_ACTIVE}
    # -- Papertrail host to which the logs will be sent
    papertrail_host: ${PAPERTRAIL_HOST}
    # -- Papertrail port to which the logs will be sent
    papertrail_port: ${PAPERTRAIL_PORT}
    # -- Timezone used for periodic jobs, timestamps...
    timezone: ${TIMEZONE}
    # -- Indicate mongo username    
    mongodb_username: ${TICKET_COLLECTOR_MONGO_USERNAME}
    # -- Indicate mongo password
    mongodb_password: ${TICKET_COLLECTOR_MONGO_PASSWORD}
    # -- Indicate mongo hostname
    mongodb_host: ${TICKET_COLLECTOR_MONGO_HOST}
    # -- Indicate mongo port to use
    mongodb_port: ${TICKET_COLLECTOR_MONGO_PORT}
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
    # -- NATS cluster endpoint
    nats_server: "nats://automation-engine-nats:4222"
    # -- Redis Hostname used to store heavy NATS messages (>1MB)
    redis_hostname: ${REDIS_HOSTNAME}
    # -- Indicates if the logs will be sent to papertrail or not.
    papertrail_active: ${PAPERTRAIL_ACTIVE}
    # -- Papertrail host to which the logs will be sent
    papertrail_host: ${PAPERTRAIL_HOST}
    # -- Papertrail port to which the logs will be sent
    papertrail_port: ${PAPERTRAIL_PORT}
    # -- Timezone used for periodic jobs, timestamps...
    timezone: ${TIMEZONE}
    # -- Indicate mongo username    
    mongodb_username: ${TICKET_COLLECTOR_MONGO_USERNAME}
    # -- Indicate mongo password
    mongodb_password: ${TICKET_COLLECTOR_MONGO_PASSWORD}
    # -- Indicate mongo hostname
    mongodb_host: ${TICKET_COLLECTOR_MONGO_HOST}
    # -- Indicate mongo port to use
    mongodb_port: ${TICKET_COLLECTOR_MONGO_PORT}
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
  resources:
    # We usually recommend not to specify default resources and to leave this as a conscious
    # choice for the user. This also increases chances charts run on environments with little
    # resources, such as Minikube. If you do want to specify resources, uncomment the following
    # lines, adjust them as necessary, and remove the curly braces after "resources:".
    limits:
      cpu: 200m
      memory: 256Mi
    requests:
      cpu: 100m
      memory: 128Mi
  autoscaling:
    enabled: ${NOTIFIER_ENABLED}
    minReplicas: ${NOTIFIER_DESIRED_TASKS}
    maxReplicas: 5
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80


# -- repair-tickets-kre-bridge subchart specific configuration
repair-tickets-kre-bridge:
  enabled: ${REPAIR_TICKETS_KRE_BRIDGE_ENABLED}
  replicaCount: ${REPAIR_TICKETS_KRE_BRIDGE_DESIRED_TASKS}
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
    # -- [Monitoring] VeloCloud hosts whose edges will be monitored
    monitoring__monitored_velocloud_hosts: ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/service-affecting/monitor/monitored-velocloud-hosts
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


# -- service-outage-monitor subchart specific configuration
service-outage-monitor:
  enabled: ${SERVICE_OUTAGE_MONITOR_ENABLED}
  replicaCount: ${SERVICE_OUTAGE_MONITOR_DESIRED_TASKS}
  config:
    # -- [Monitoring] VeloCloud hosts whose edges will be monitored
    monitoring__monitored_velocloud_hosts: ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/service-outage/monitor/monitored-velocloud-hosts
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


# -- servicenow-bridge subchart specific configuration
servicenow-bridge:
  # -- Field to indicate if the servicenow-bridge module is going to be deployed
  enabled: ${SERVICENOW_BRIDGE_ENABLED}
  # -- Number of servicenow-bridge pods
  replicaCount: ${SERVICENOW_BRIDGE_DESIRED_TASKS}
  image:
    # -- Repository image for servicenow-bridge module
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/servicenow-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${SERVICENOW_BRIDGE_BUILD_NUMBER}
  # -- Service Configuration
  service:
    type: ClusterIP
    port: 5000
  # servicenow-bridge specific configuration variables
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
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/t7-bridge
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${T7_BRIDGE_BUILD_NUMBER}
  imagePullSecrets: []
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
    # -- Indicates if the logs will be sent to papertrail or not.
    papertrail_active: ${PAPERTRAIL_ACTIVE}
    # -- Papertrail host to which the logs will be sent
    papertrail_host: ${PAPERTRAIL_HOST}
    # -- Papertrail port to which the logs will be sent
    papertrail_port: ${PAPERTRAIL_PORT}
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
    # -- Redis Hostname used to store heavy NATS messages (>1MB)
    redis_hostname: ${REDIS_HOSTNAME}
    # -- Indicates if the logs will be sent to papertrail or not.
    papertrail_active: ${PAPERTRAIL_ACTIVE}
    # -- Papertrail host to which the logs will be sent
    papertrail_host: ${PAPERTRAIL_HOST}
    # -- Papertrail port to which the logs will be sent
    papertrail_port: ${PAPERTRAIL_PORT}
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
    # -- VeloCloud hosts whose edges will be monitored
    monitored_velocloud_hosts: ref+awsssm://automation-engine/${CURRENT_ENVIRONMENT_SHORT}/tnba-monitor/monitored-velocloud-hosts
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
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 192Mi


# -- velocloud-bridge subchart specific configuration
velocloud-bridge:
  enabled: ${VELOCLOUD_BRIDGE_ENABLED}
  replicaCount: ${VELOCLOUD_BRIDGE_DESIRED_TASKS}
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


# -- velocloud-gateway-monitor subchart specific configuration
velocloud-gateway-monitor:
  enabled: ${VELOCLOUD_GATEWAY_MONITOR_ENABLED}
  replicaCount: ${VELOCLOUD_GATEWAY_MONITOR_DESIRED_TASKS}
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
  image:
    repository: 374050862540.dkr.ecr.us-east-1.amazonaws.com/velocloud-gateway-monitor
    pullPolicy: Always
    # Overrides the image tag whose default is the chart appVersion.
    tag: ${VELOCLOUD_GATEWAY_MONITOR_BUILD_NUMBER}
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
    enabled: ${VELOCLOUD_GATEWAY_MONITOR_ENABLED}
    minReplicas: ${VELOCLOUD_GATEWAY_MONITOR_DESIRED_TASKS}
    maxReplicas: 3
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80