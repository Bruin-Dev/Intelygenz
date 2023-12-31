#!/bin/bash
apk update && apk add coreutils

if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
  export MODULE_NAME=$ECR_REPOSITORY_NAME
  export ENVIRONMENT_ID=$(echo -n "${CI_COMMIT_REF_SLUG}" | sha256sum | cut -c1-8)
  export ENVIRONMENT_VAR="automation-${ENVIRONMENT_ID}"
  export CURRENT_ENVIRONMENT="dev"
  export TAG="${ENVIRONMENT_ID}-${CI_PIPELINE_ID}"
  export DOCKER_BUILD_LATEST_TAG="${ENVIRONMENT_ID}-latest"
  export DNS_ENVIRONMENT_VAR="https://${ENVIRONMENT_ID}.mettel-automation.net"
  # prometheus environment variables for dev environment
  export PROMETHEUS_INGRESS_HOSTNAME="prometheus-${TF_VAR_CURRENT_ENVIRONMENT}.mettel-automation.net"
  export PROMETHEUS_INGRESS_EXTERNAL_URL="https://${PROMETHEUS_INGRESS_HOSTNAME}"
  export GRAFANA_INGRESS_HOSTNAME="grafana-${TF_VAR_CURRENT_ENVIRONMENT}.mettel-automation.net"
  export GRAFANA_INGRESS_ROOT_URL="https://${GRAFANA_INGRESS_HOSTNAME}"
  export ECR_REPOSITORY_TAG="${TAG}"
else
  export MODULE_NAME=$ECR_REPOSITORY_NAME
  export ENVIRONMENT_ID="production"
  export ENVIRONMENT_VAR="automation-master"
  export TAG=$(git tag | sort --version-sort | grep "^${ECR_REPOSITORY_NAME}" | tail -n -1| cut -d "@" -f2)
  export DOCKER_BUILD_LATEST_TAG="latest"
  export DNS_ENVIRONMENT_VAR="https://master.mettel-automation.net"
  # prometheus environment variables for production environment
  export PROMETHEUS_INGRESS_HOSTNAME="prometheus.mettel-automation.net"
  export PROMETHEUS_INGRESS_EXTERNAL_URL="https://${PROMETHEUS_INGRESS_HOSTNAME}"
  export GRAFANA_INGRESS_HOSTNAME="grafana.mettel-automation.net"
  export GRAFANA_INGRESS_ROOT_URL="https://${GRAFANA_INGRESS_HOSTNAME}"
  export ECR_REPOSITORY_TAG=${TAG}
fi
