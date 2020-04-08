#!/bin/bash
    
export TF_VAR_BRUIN_BRIDGE_BUILD_NUMBER=$(cat /tmp/automation-bruin-bridge.json| jq -r .tag)
echo "TF_VAR_BRUIN_BRIDGE_BUILD_NUMBER is ${TF_VAR_BRUIN_BRIDGE_BUILD_NUMBER}"
export TF_VAR_LIT_BRIDGE_BUILD_NUMBER=$(cat /tmp/automation-lit-bridge.json| jq -r .tag)
echo "TF_VAR_LIT_BRIDGE_BUILD_NUMBER is ${TF_VAR_LIT_BRIDGE_BUILD_NUMBER}"
export TF_VAR_LAST_CONTACT_REPORT_BUILD_NUMBER=$(cat /tmp/automation-last-contact-report.json| jq -r .tag)
echo "TF_VAR_LAST_CONTACT_REPORT_BUILD_NUMBER is ${TF_VAR_LAST_CONTACT_REPORT_BUILD_NUMBER}"
export TF_VAR_GRAFANA_BUILD_NUMBER=$(cat /tmp/grafana.json | jq -r .tag)
echo "TF_VAR_GRAFANA_BUILD_NUMBER is ${TF_VAR_GRAFANA_BUILD_NUMBER}"
export TF_VAR_PROMETHEUS_BUILD_NUMBER=$(cat /tmp/prometheus.json | jq -r .tag)
echo "TF_VAR_PROMETHEUS_BUILD_NUMBER is ${TF_VAR_PROMETHEUS_BUILD_NUMBER}"
export TF_VAR_THANOS_BUILD_NUMBER=$(cat /tmp/thanos.json | jq -r .tag)
echo "TF_VAR_THANOS_BUILD_NUMBER is ${TF_VAR_THANOS_BUILD_NUMBER}"
export TF_VAR_THANOS_QUERIER_BUILD_NUMBER=$(cat /tmp/thanos-querier.json | jq -r .tag)
echo "TF_VAR_THANOS_QUERIER_BUILD_NUMBER is ${TF_VAR_THANOS_QUERIER_BUILD_NUMBER}"
export TF_VAR_THANOS_STORE_GATEWAY_BUILD_NUMBER=$(cat /tmp/thanos-store-gateway.json | jq -r .tag)
echo "TF_VAR_THANOS_STORE_GATEWAY_BUILD_NUMBER is ${TF_VAR_THANOS_STORE_GATEWAY_BUILD_NUMBER}"
export TF_VAR_NATS_SERVER_BUILD_NUMBER=$(cat /tmp/automation-nats-server.json | jq -r .tag)
echo "TF_VAR_NATS_SERVER_BUILD_NUMBER is ${TF_VAR_NATS_SERVER_BUILD_NUMBER}"
export TF_VAR_NOTIFIER_BUILD_NUMBER=$(cat /tmp/automation-notifier.json | jq -r .tag)
echo "TF_VAR_NOTIFIER_BUILD_NUMBER is ${TF_VAR_NOTIFIER_BUILD_NUMBER}"
export TF_VAR_SERVICE_AFFECTING_MONITOR_BUILD_NUMBER=$(cat /tmp/automation-service-affecting-monitor.json | jq -r .tag)
echo "TF_VAR_SERVICE_AFFECTING_MONITOR_BUILD_NUMBER is ${TF_VAR_SERVICE_AFFECTING_MONITOR_BUILD_NUMBER}"
export TF_VAR_SERVICE_OUTAGE_MONITOR_BUILD_NUMBER=$(cat /tmp/automation-service-outage-monitor.json | jq -r .tag)
echo "TF_VAR_SERVICE_OUTAGE_MONITOR_BUILD_NUMBER is ${TF_VAR_SERVICE_OUTAGE_MONITOR_BUILD_NUMBER}"
export TF_VAR_SITES_MONITOR_BUILD_NUMBER=$(cat /tmp/automation-sites-monitor.json | jq -r .tag)
echo "TF_VAR_SITES_MONITOR_BUILD_NUMBER is ${TF_VAR_SITES_MONITOR_BUILD_NUMBER}"
export TF_VAR_T7_BRIDGE_BUILD_NUMBER=$(cat /tmp/automation-t7-bridge.json | jq -r .tag)
echo "TF_VAR_T7_BRIDGE_BUILD_NUMBER is ${TF_VAR_T7_BRIDGE_BUILD_NUMBER}"
export TF_VAR_VELOCLOUD_BRIDGE_BUILD_NUMBER=$(cat /tmp/automation-velocloud-bridge.json | jq -r .tag)
echo "TF_VAR_VELOCLOUD_BRIDGE_BUILD_NUMBER is ${TF_VAR_VELOCLOUD_BRIDGE_BUILD_NUMBER}"