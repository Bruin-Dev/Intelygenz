context_name: main

contexts:
  main:
    url: ${CI_ENVIRONMENT_URL}
    user_name: admin
    password: ${GRAFANA_ADMIN_PASSWORD}
    ignore_filters: False  # When set to true all Watched filtered folders will be ignored and ALL folders will be acted on
    watched:
      - bruin

global:
  debug: true
  ignore_ssl_errors: false