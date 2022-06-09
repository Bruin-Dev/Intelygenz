## kube-prometheus-stack submodule
kubeprometheusstack:
  ## Labels to apply to all resources
  commonLabels:
    mettel-automation-mon: "true"
  ## Create default rules for monitoring the cluster
  defaultRules:
    create: true

  ## Configuration for alertmanager
  ## ref: https://prometheus.io/docs/alerting/alertmanager/
  alertmanager:
    enabled: false
    ## TODO: Configure alermanager using nginx ingress
    ingress:
      enabled: true
      hosts: [ 'alertz.k8s.igzdev.com' ]
      #ingressClassName: traefik
      annotations:
        traefik.ingress.kubernetes.io/router.entrypoints: web, websecure
        traefik.ingress.kubernetes.io/router.middlewares: tools-system-redirectscheme@kubernetescrd, prometheus-authalertmanager@kubernetescrd
        cert-manager.io/cluster-issuer: issuer-production-cert-manager-issuer
      tls:
        - secretName: alertz-server-tls
          hosts:
            - alertz.k8s.igzdev.com

    ## Alertmanager configuration directives
    ## ref: https://prometheus.io/docs/alerting/configuration/#configuration-file
    ##      https://prometheus.io/webtools/alerting/routing-tree-editor/
    config:
      global:
        resolve_timeout: 5m
      route:
        group_by: [ 'alertname', 'job', 'target' ]
        group_wait: 30s
        group_interval: 5m
        repeat_interval: 24h
        receiver: 'null'
        routes:
          - match:
              alertname: Watchdog
            receiver: 'null'
      receivers:
        - name: 'null'
      templates:
        - '*.tmpl'

    templateFiles:
      slack.tmpl: |-
        {{ define "__alert_silence_link" -}}
          {{ .ExternalURL }}/#/silences/new?filter={alertname%3D"{{ .CommonLabels.alertname }}"{{ if .CommonLabels.target }}%2Ctarget%3D"{{ .CommonLabels.target }}{{ end }}"}
        {{- end }}

        {{ define "__alert_severity_prefix" -}}
          {{ if ne .Status "firing" -}}
            :thumbsup:
          {{- else if eq .Labels.severity "critical" -}}
            :fire:
          {{- else if eq .Labels.severity "warning" -}}
            :warning:
          {{- else if eq .Labels.severity "info" -}}
            :information_source:
          {{- else -}}
            :question:
          {{- end }}
        {{- end }}

        {{ define "__alert_severity_prefix_title" -}}
          {{ if ne .Status "firing" -}}
            :thumbsup:
          {{- else if eq .CommonLabels.severity "critical" -}}
            :fire:
          {{- else if eq .CommonLabels.severity "warning" -}}
            :warning:
          {{- else if eq .CommonLabels.severity "info" -}}
            :information_source:
          {{- else -}}
            :question:
          {{- end }}
        {{- end }}

        {{ define "__slack_channel_name" -}}
          {{ if eq .CommonLabels.severity "critical" -}}
            igz-critical-alerts
          {{- else -}}
            igz-alerts
          {{- end }}
        {{- end }}

        {{ define "monzo.slack.title" -}}
          [{{ .Status | toUpper -}}
          {{ if eq .Status "firing" }}{{- end -}}
          ] {{ template "__alert_severity_prefix_title" . }} {{ title (index .Alerts 0).Labels.environment }}{{ .CommonLabels.alertname }}
        {{- end }}

        {{ define "monzo.slack.color" -}}
          {{ if eq .Status "firing" -}}
            {{ if eq .CommonLabels.severity "warning" -}}
              warning
            {{- else if eq .CommonLabels.severity "critical" -}}
              danger
            {{- else -}}
              #439FE0
            {{- end -}}
          {{ else -}}
          good
          {{- end }}
        {{- end }}

        {{ define "monzo.slack.icon_emoji" }}:prometheus:{{ end }}

        {{ define "monzo.slack.description" -}}
          {{ if index ((index .Alerts 0).Annotations) "summary" -}}
            {{ index ((index .Alerts 0).Annotations) "summary" }}
          {{- end }}
          {{ if index ((index .Alerts 0).Annotations) "message" -}}
            {{ index ((index .Alerts 0).Annotations) "message" }}
          {{ end }}
        {{- end }}

        {{ define "monzo.slack.grafana" -}}
          {{ if ne (index ((index .Alerts 0).Annotations) "grafana") "" -}}
            {{ index ((index .Alerts 0).Annotations) "grafana" }}
          {{- end }}
        {{- end }}

    ## Settings affecting alertmanagerSpec
    ## ref: https://github.com/prometheus-operator/prometheus-operator/blob/master/Documentation/api.md#alertmanagerspec
    alertmanagerSpec:
      alertmanagerConfigSelector:
        matchLabels:
          igz-mon: "true"

      externalUrl: "https://alertz.k8s.igzdev.com"

      # <<: *nodeSelectorTolerations
  ## Using default values from https://github.com/grafana/helm-charts/blob/main/charts/grafana/values.yaml
  ## TODO: Configure grafana using nginx ingress and include specific dashboards
  grafana:
    enabled: true
    defaultDashboardsEnabled: true
    ingress:
      enabled: true
      hosts: [ '${GRAFANA_INGRESS_HOSTNAME}' ]
      ingressClassName: nginx

    admin:
      existingSecret: auth-grafana
      userKey: user
      passwordKey: password

    plugins:
      - grafana-piechart-panel
      - grafana-polystat-panel

    sidecar:
      dashboards:
        enabled: true
        label: grafana_dashboard
        folderAnnotation: grafana_folder
        folder: /tmp/dashboards
        provider:
          name: default
          orgId: 1
          folder: 'general'
          type: file
          disableDelete: true
          allowUiUpdates: false
          foldersFromFilesStructure: true

      datasources:
        enabled: true
        defaultDatasourceEnabled: true
        label: grafana_datasource

    ## (custom) Grafana Dashboards
    ## name of dashboard without extension
    grafanaDashboards:
      - bruin-api-usage
      - business-metrics-intermapper
      - business-metrics-sd-wan
      - business-metrics-service-affecting
      - business-metrics-service-outage
      - datahighway-kafka
      - mettel-current-sdwan-status
      - nats-statistics

    grafana.ini:
      server:
        # The full public facing url you use in browser, used for redirects and emails
        root_url: ${GRAFANA_INGRESS_ROOT_URL}
      auth.google:
        enabled: true
        client_id: ${GOOGLE_OAUTH_CLIENT_ID}
        client_secret: ${GOOGLE_OAUTH_CLIENT_SECRET}
        scopes: https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email
        auth_url: https://accounts.google.com/o/oauth2/auth
        token_url: https://accounts.google.com/o/oauth2/token
        allowed_organizations: intelygenz.com
        allow_sign_up: true

      # <<: *nodeSelectorTolerations

  ## Components to scraper
  kubeApiServer:
    enabled: true
  kubelet:
    enabled: true
  kubeControllerManager:
    enabled: true
  coreDns:
    enabled: true
  kubeDns:
    enabled: true
  kubeEtcd:
    enabled: true
  kubeScheduler:
    enabled: true
  kubeProxy:
    enabled: true
  kubeStateMetrics:
    enabled: true
  nodeExporter:
    enabled: true
    jobLabel: node-exporter
    serviceMonitor:
      relabelings:
        - targetLabel: job
          replacement: node-exporter
  prometheus-node-exporter:
    podLabels:
      jobLabel: node-exporter
    extraArgs:
      - --collector.filesystem.ignored-mount-points=^/(dev|proc|sys|var/lib/docker/.+|var/lib/kubelet/.+)($|/)
      - --collector.filesystem.ignored-fs-types=^(autofs|binfmt_misc|bpf|cgroup2?|configfs|debugfs|devpts|devtmpfs|fusectl|hugetlbfs|iso9660|mqueue|nsfs|overlay|proc|procfs|pstore|rpc_pipefs|securityfs|selinuxfs|squashfs|sysfs|tracefs)$

  ## Manages Prometheus and Alertmanager components
  prometheusOperator:
    enabled: true

  ## Deploy a Prometheus instance
  prometheus:
    enabled: true
    ingress:
      enabled: true
      hosts: [ '${PROMETHEUS_INGRESS_HOSTNAME}' ]
      ingressClassName: nginx
    ## Configuration for Prometheus service
    prometheusSpec:
      scrapeInterval: 30s
      scrapeTimeout: 15s
      enableAdminAPI: true

      externalUrl: "${PROMETHEUS_INGRESS_EXTERNAL_URL}"

      ruleSelectorNilUsesHelmValues: true
      serviceMonitorSelectorNilUsesHelmValues: false
      podMonitorSelectorNilUsesHelmValues: false

      ## Select all prometheusrules resources
      ruleSelector:
        matchLabels:
          mettel-automation-mon: "true"

      retention: 30d
      walCompression: true

      ## storage
      storageSpec:
        volumeClaimTemplate:
          spec:
            storageClassName: gp2
            resources:
              requests:
                storage: 50Gi
      
      ## Metrics from data-higway
      #### ca certificate to scrape kafka metrics
      configMaps: 
        - ca-pemstore
      #### configuration for scrape metrics
      additionalScrapeConfigs:
        - job_name: 'kafka-data-highway'
          scrape_interval: 5s
          scrape_timeout: 5s
          scheme: https
          basic_auth:
            username: ${KAFKA_METRICS_USER}
            password: ${KAFKA_METRICS_PASSWORD}
          static_configs:
            - targets: [ '${KAFKA_METRICS_URL}' ]
              labels:
                project: 'data-highway'
                service: 'kafka'
          tls_config:
            ca_file: /etc/prometheus/configmaps/ca-pemstore/aivencloud-project-ca-certificate.pem
        - job_name: 'kafka-connect-data-highway'
          scrape_interval: 5s
          scrape_timeout: 5s
          scheme: https
          basic_auth:
            username: ${KAFKA_CONNECT_METRICS_USER}
            password: ${KAFKA_CONNECT_METRICS_PASSWORD}
          static_configs:
            - targets: [ '${KAFKA_CONNECT_METRICS_URL}' ]
              labels:
                project: 'data-highway'
                service: 'kafka-connect'
          tls_config:
            ca_file: /etc/prometheus/configmaps/ca-pemstore/aivencloud-project-ca-certificate.pem
        - job_name: 'data-highway-velocloud-fetcher'
          scrape_interval: 5s
          scrape_timeout: 5s
          scheme: http
          static_configs:
            - targets: [ '${DATA_HIGHWAY_VELOCLOUD_FETCHER_METRICS_URL}' ]
              labels:
                project: 'data-highway'
                service: 'velocloud-fetcher'