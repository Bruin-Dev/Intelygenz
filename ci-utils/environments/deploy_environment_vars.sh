#!/bin/bash

function common_variables_by_environment() {
  export TIMEZONE=${TIMEZONE}

  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # common variables for ephemeral environments
    export LAST_CONTACT_RECIPIENT=${LAST_CONTACT_RECIPIENT_DEV}
    export KRE_TNBA_BASE_URL=${KRE_TNBA_BASE_URL_DEV}
    export KRE_REPAIR_TICKETS_BASE_URL=${KRE_REPAIR_TICKETS_BASE_URL_DEV}
    export REDIS_HOSTNAME=${REDIS_HOSTNAME_DEV}
    export REDIS_CUSTOMER_CACHE_HOSTNAME=${REDIS_CUSTOMER_CACHE_HOSTNAME_DEV}
    export REDIS_TNBA_FEEDBACK_HOSTNAME=${REDIS_TNBA_FEEDBACK_HOSTNAME_DEV}
    export REDIS_EMAIL_TAGGER_HOSTNAME=${REDIS_EMAIL_TAGGER_HOSTNAME_DEV}
    export PAPERTRAIL_HOST=${PAPERTRAIL_HOST_DEV}
    export PAPERTRAIL_PORT=${PAPERTRAIL_PORT_DEV}
    export PAPERTRAIL_API_TOKEN=${PAPERTRAIL_API_TOKEN_DEV}
    export PAPERTRAIL_ACTIVE="false"
  else
    # common environment variables for production environment
    export LAST_CONTACT_RECIPIENT=${LAST_CONTACT_RECIPIENT_PRO}
    export KRE_TNBA_BASE_URL=${KRE_TNBA_BASE_URL_PRO}
    export KRE_REPAIR_TICKETS_BASE_URL=${KRE_REPAIR_TICKETS_BASE_URL_PRO}
    export REDIS_HOSTNAME=${REDIS_HOSTNAME_PRO}
    export REDIS_CUSTOMER_CACHE_HOSTNAME=${REDIS_CUSTOMER_CACHE_HOSTNAME_PRO}
    export REDIS_TNBA_FEEDBACK_HOSTNAME=${REDIS_TNBA_FEEDBACK_HOSTNAME_PRO}
    export REDIS_EMAIL_TAGGER_HOSTNAME=${REDIS_EMAIL_TAGGER_HOSTNAME_PRO}
    export PAPERTRAIL_HOST=${PAPERTRAIL_HOST_PRO}
    export PAPERTRAIL_PORT=${PAPERTRAIL_PORT_PRO}
    export PAPERTRAIL_API_TOKEN=${PAPERTRAIL_API_TOKEN_PRO}
    export PAPERTRAIL_ACTIVE="true"
  fi
}

function bruin_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # bruin-bridge environment variables for ephemeral environments
    export BRUIN_BRIDGE__BRUIN_LOGIN_URL="${DEV__BRUIN_BRIDGE__LOGIN_URL}"
    export BRUIN_BRIDGE__BRUIN_BASE_URL="${DEV__BRUIN_BRIDGE__BASE_URL}"
    export BRUIN_BRIDGE__BRUIN_CLIENT_ID="${DEV__BRUIN_BRIDGE__CLIENT_ID}"
    export BRUIN_BRIDGE__BRUIN_CLIENT_SECRET="${DEV__BRUIN_BRIDGE__CLIENT_SECRET}"
    export BRUIN_BRIDGE__BRUIN_LOGIN_URL_IP="${DEV__BRUIN_BRIDGE__LOGIN_URL_IP}"
    export BRUIN_BRIDGE__BRUIN_BASE_URL_IP="${DEV__BRUIN_BRIDGE__BASE_URL_IP}"
  else
    # bruin-bridge environment variables for production environment
    export BRUIN_BRIDGE__BRUIN_LOGIN_URL="${PRO__BRUIN_BRIDGE__LOGIN_URL}"
    export BRUIN_BRIDGE__BRUIN_BASE_URL="${PRO__BRUIN_BRIDGE__BASE_URL}"
    export BRUIN_BRIDGE__BRUIN_CLIENT_ID="${PRO__BRUIN_BRIDGE__CLIENT_ID}"
    export BRUIN_BRIDGE__BRUIN_CLIENT_SECRET="${PRO__BRUIN_BRIDGE__CLIENT_SECRET}"
  fi
}

function customer_cache_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # customer-cache environment variables for ephemeral environments
    export CUSTOMER_CACHE__VELOCLOUD_HOSTS="$(echo "${DEV__CUSTOMER_CACHE__VELOCLOUD_HOSTS}" | jq . -c)"
    export CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT="${DEV__CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}"
    export CUSTOMER_CACHE__REFRESH_JOB_INTERVAL="${DEV__CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}"
    export CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL="${DEV__CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL}"
    export CUSTOMER_CACHE__BLACKLISTED_EDGES="$(echo "${DEV__CUSTOMER_CACHE__BLACKLISTED_EDGES}" | jq . -c)"
    export CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS="$(echo "${DEV__CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS}" | jq . -c)"
    export CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES="$(echo "${DEV__CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}" | jq . -c)"
  else
    # customer-cache environment variables for production environment
    export CUSTOMER_CACHE__VELOCLOUD_HOSTS="$(echo "${PRO__CUSTOMER_CACHE__VELOCLOUD_HOSTS}" | jq . -c)"
    export CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT="${PRO__CUSTOMER_CACHE__DUPLICATE_INVENTORIES_RECIPIENT}"
    export CUSTOMER_CACHE__REFRESH_JOB_INTERVAL="${PRO__CUSTOMER_CACHE__REFRESH_JOB_INTERVAL}"
    export CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL="${PRO__CUSTOMER_CACHE__REFRESH_CHECK_INTERVAL}"
    export CUSTOMER_CACHE__BLACKLISTED_EDGES="$(echo "${PRO__CUSTOMER_CACHE__BLACKLISTED_EDGES}" | jq . -c)"
    export CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS="$(echo "${PRO__CUSTOMER_CACHE__BLACKLISTED_CLIENTS_WITH_PENDING_STATUS}" | jq . -c)"
    export CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES="$(echo "${PRO__CUSTOMER_CACHE__WHITELISTED_MANAGEMENT_STATUSES}" | jq . -c)"
  fi
}

function digi_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # digi-bridge environment variables for ephemeral environments
    export DIGI_BRIDGE__DIGI_REBOOT_API_BASE_URL="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_BASE_URL}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_ID="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_ID}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_SECRET="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_SECRET}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_TOKEN_TTL="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_TOKEN_TTL}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_IP="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_IP}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_DNS_RECORD_NAME="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_DNS_RECORD_NAME}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_TEST_IP="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_TEST_IP}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_TEST_DNS_RECORD_NAME="${DEV__DIGI_BRIDGE__DIGI_REBOOT_API_TEST_DNS_RECORD_NAME}"
  else
    # digi-bridge environment variables for production environment
    export DIGI_BRIDGE__DIGI_REBOOT_API_BASE_URL="${PRO__DIGI_BRIDGE__DIGI_REBOOT_API_BASE_URL}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_ID="${PRO__DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_ID}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_SECRET="${PRO__DIGI_BRIDGE__DIGI_REBOOT_API_CLIENT_SECRET}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_TOKEN_TTL="${PRO__DIGI_BRIDGE__DIGI_REBOOT_API_TOKEN_TTL}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_IP="${PRO__DIGI_BRIDGE__DIGI_REBOOT_API_IP}"
    export DIGI_BRIDGE__DIGI_REBOOT_API_DNS_RECORD_NAME="${PRO__DIGI_BRIDGE__DIGI_REBOOT_API_DNS_RECORD_NAME}"
  fi
}

function digi_reboot_report_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # digi-reboot-report environment variables for ephemeral environments
    export DIGI_REBOOT_REPORT__REPORT_JOB_INTERVAL="${DEV__DIGI_REBOOT_REPORT__REPORT_JOB_INTERVAL}"
    export DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL="${DEV__DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL}"
    export DIGI_REBOOT_REPORT__REPORT_RECIPIENT="${DEV__DIGI_REBOOT_REPORT__REPORT_RECIPIENT}"
  else
    # digi-reboot-report environment variables for production environment
    export DIGI_REBOOT_REPORT__REPORT_JOB_INTERVAL="${PRO__DIGI_REBOOT_REPORT__REPORT_JOB_INTERVAL}"
    export DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL="${PRO__DIGI_REBOOT_REPORT__LOGS_LOOKUP_INTERVAL}"
    export DIGI_REBOOT_REPORT__REPORT_RECIPIENT="${PRO__DIGI_REBOOT_REPORT__REPORT_RECIPIENT}"
  fi
}

function dri_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # dri-bridge environment variables for ephemeral environments
    export DRI_ACC_EMAIL="${DRI_ACC_EMAIL_DEV}"
    export DRI_ACC_PASSWORD="${DRI_ACC_PASSWORD_DEV}"
    export DRI_BASE_URL="${DRI_BASE_URL_DEV}"
  else
    # dri-bridge environment variables for production environment
    export DRI_ACC_EMAIL="${DRI_ACC_EMAIL_PRO}"
    export DRI_ACC_PASSWORD="${DRI_ACC_PASSWORD_PRO}"
    export DRI_BASE_URL="${DRI_BASE_URL_PRO}"
  fi
}

function email_tagger_kre_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # email-tagger-kre-bridge environment variables for ephemeral environments
    export EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL="${DEV__EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL}"
  else
    # email-tagger-kre-bridge environment variables for production environment
    export EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL="${PRO__EMAIL_TAGGER_KRE_BRIDGE__KRE_BASE_URL}"
  fi
}

function email_tagger_monitor_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # email-tagger-monitor environment variables for ephemeral environments
    export EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL="${DEV__EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL}"
    export EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL="${DEV__EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL}"
    export EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS="${DEV__EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS}"
    export EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS="${DEV__EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS}"
    export EMAIL_TAGGER_MONITOR__API_REQUEST_KEY="${DEV__EMAIL_TAGGER_MONITOR__API_REQUEST_KEY}"
    export EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY="${DEV__EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY}"
    export EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX="${DEV__EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX}"
  else
    # email-tagger-monitor environment variables for production environment
    export EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL="${PRO__EMAIL_TAGGER_MONITOR__NEW_EMAILS_JOB_INTERVAL}"
    export EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL="${PRO__EMAIL_TAGGER_MONITOR__NEW_TICKETS_JOB_INTERVAL}"
    export EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS="${PRO__EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_EMAILS}"
    export EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS="${PRO__EMAIL_TAGGER_MONITOR__MAX_CONCURRENT_TICKETS}"
    export EMAIL_TAGGER_MONITOR__API_REQUEST_KEY="${PRO__EMAIL_TAGGER_MONITOR__API_REQUEST_KEY}"
    export EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY="${PRO__EMAIL_TAGGER_MONITOR__API_REQUEST_SIGNATURE_SECRET_KEY}"
    export EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX="${PRO__EMAIL_TAGGER_MONITOR__API_ENDPOINT_PREFIX}"
  fi
}

function hawkeye_affecting_monitor_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # hawkeye-affecting-monitor environment variables for ephemeral environments
    export HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL="${DEV__HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL}"
    export HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL="${DEV__HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL}"
    export HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY="${DEV__HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY}"
  else
    # hawkeye-affecting-monitor environment variables for production environment
    export HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL="${PRO__HAWKEYE_AFFECTING_MONITOR__MONITORING_JOB_INTERVAL}"
    export HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL="${PRO__HAWKEYE_AFFECTING_MONITOR__PROBES_TESTS_RESULTS_LOOKUP_INTERVAL}"
    export HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY="${PRO__HAWKEYE_AFFECTING_MONITOR__MONITORED_PRODUCT_CATEGORY}"
  fi
}

function hawkeye_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # hawkeye-bridge environment variables for ephemeral environments
    export HAWKEYE_BRIDGE__CLIENT_USERNAME="${DEV__HAWKEYE_BRIDGE__CLIENT_USERNAME}"
    export HAWKEYE_BRIDGE__CLIENT_PASSWORD="${DEV__HAWKEYE_BRIDGE__CLIENT_PASSWORD}"
    export HAWKEYE_BRIDGE__BASE_URL="${DEV__HAWKEYE_BRIDGE__BASE_URL}"
  else
    # hawkeye-bridge environment variables for production environment
    export HAWKEYE_BRIDGE__CLIENT_USERNAME="${PRO__HAWKEYE_BRIDGE__CLIENT_USERNAME}"
    export HAWKEYE_BRIDGE__CLIENT_PASSWORD="${PRO__HAWKEYE_BRIDGE__CLIENT_PASSWORD}"
    export HAWKEYE_BRIDGE__BASE_URL="${PRO__HAWKEYE_BRIDGE__BASE_URL}"
  fi
}

function links_metrics_api_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # links-metris-api environment variables for ephemeral environments
    export LINKS_METRICS_API_WHITELIST_ACCESS=${LINKS_METRICS_API_WHITELIST_ACCESS_PRO}
    export TICKET_COLLECTOR_MONGO_PORT=${TICKET_COLLECTOR_MONGO_PORT_PRO}
    export OREILLY_SECURITY_GROUP_ID=${OREILLY_SECURITY_GROUP_ID_DEV}
    export AUTOMATION_SSL_CERTIFICATE_ARN=${AUTOMATION_SSL_CERTIFICATE_ARN}
  else
    # links-metris-api environment variables for production environment
    export LINKS_METRICS_API_WHITELIST_ACCESS=${LINKS_METRICS_API_WHITELIST_ACCESS_PRO}
    export TICKET_COLLECTOR_MONGO_PORT=${TICKET_COLLECTOR_MONGO_PORT_PRO}
    export OREILLY_SECURITY_GROUP_ID=${OREILLY_SECURITY_GROUP_ID_PRO}
    export AUTOMATION_SSL_CERTIFICATE_ARN=${AUTOMATION_SSL_CERTIFICATE_ARN}
  fi
}

function lumin_billing_report_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # lumin-billing-report environment variables for ephemeral environments
    export BILLING_RECIPIENT=${BILLING_RECIPIENT_REPORT_DEV}
  else
    # lumin-billing-report environment variables for production environment
    export BILLING_RECIPIENT=${BILLING_RECIPIENT_REPORT_PROD}
  fi
}

function notifier_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # notifier environment variables for ephemeral environments
    export NOTIFIER_SLACK_URL=${SLACK_URL_DEV}
  else
    # notifier environment variables for production environment
    export NOTIFIER_SLACK_URL=${SLACK_URL_PRO}
  fi
}

function service_affecting_monitor_variables() {
  export EXEC_MONITOR_REPORTS_ON_START=${EXEC_MONITOR_REPORTS_ON_START}
  export EXEC_BANDWIDTH_REPORTS_ON_START=${EXEC_BANDWIDTH_REPORTS_ON_START}

  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # service-affecting-monitor environment variables for ephemeral environments
    : # noop
  else
    # service-affecting-monitor environment variables for production environment
    : # noop
  fi
}

function service_outage_monitor_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # service-outage-monitor (SOM) environment variables for ephemeral environments
    export SOM_MONITORED_VELOCLOUD_HOSTS="${SOM_MONITORED_VELOCLOUD_HOSTS_DEV}"
  else
    # service-outage-monitor (SOM) environment variables for production environment
    export SOM_MONITORED_VELOCLOUD_HOSTS="${SOM_MONITORED_VELOCLOUD_HOSTS_PRO}"
  fi
}

function t7_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # t7-bridge environment variables for ephemeral environments
    export T7_BASE_URL=${T7_BASE_URL_DEV}
    export T7_TOKEN=${T7_TOKEN_DEV}
  else
    # t7-bridge environment variables for production environment
    export T7_BASE_URL=${T7_BASE_URL_PRO}
    export T7_TOKEN=${T7_TOKEN_PRO}
  fi
}

function ticket_collector_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # ticket-collector environment variables for ephemeral environments
    export TICKET_COLLECTOR_MONGO_USERNAME="user"
    export TICKET_COLLECTOR_MONGO_PASSWORD="mypassword"
    export TICKET_COLLECTOR_MONGO_HOST="docdb"
    export TICKET_COLLECTOR_MONGO_DB_NAME="mydb"
  else
    # ticket-collector environment variables for production environment
    export TICKET_COLLECTOR_MONGO_USERNAME=${TICKET_COLLECTOR_MONGO_USERNAME}
    export TICKET_COLLECTOR_MONGO_PASSWORD=${TICKET_COLLECTOR_MONGO_PASSWORD}
    export TICKET_COLLECTOR_MONGO_HOST=${TICKET_COLLECTOR_MONGO_HOST}
    export TICKET_COLLECTOR_MONGO_DB_NAME=${TICKET_COLLECTOR_MONGO_DB_NAME}
  fi
}

function velocloud_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # velocloud-bridge environment variables for ephemeral environments
    export VELOCLOUD_BRIDGE__VELOCLOUD_CREDENTIALS="${DEV__VELOCLOUD_BRIDGE__VELOCLOUD_CREDENTIALS}"
  else
    # velocloud-bridge environment variables for production environment
    export VELOCLOUD_BRIDGE__VELOCLOUD_CREDENTIALS="${PRO__VELOCLOUD_BRIDGE__VELOCLOUD_CREDENTIALS}"
  fi
}

function create_enabled_var_for_each_subchart() {
  # Create dinamically enabled value for each subchart in an environment variable
  for environment_var in $(env | grep "_DESIRED"); do
    MODULE_DESIRED_TASKS_NAME=$(echo "${environment_var}" | awk -F "=" '{print $1}')
    MODULE_DESIRED_TASKS_VALUE=$(echo "${environment_var}" | awk -F "=" '{print $2}')
    MODULE_ENABLED_VARIABLE="$(printf '%s\n' "${MODULE_DESIRED_TASKS_NAME//_DESIRED_TASKS/}" | awk '{ print toupper($0) }')_ENABLED"
    if [ "$MODULE_DESIRED_TASKS_VALUE" -gt "0" ]; then
      export "${MODULE_ENABLED_VARIABLE}=true"
    else
      export "${MODULE_ENABLED_VARIABLE}=false"
    fi
  done
}

function environments_assign() {
  # assign enabled variable for each subchart
  create_enabled_var_for_each_subchart
  # assign common environment variables for each environment
  common_variables_by_environment
  # assign specific environment variables for each subchart
  bruin_bridge_variables
  customer_cache_variables
  digi_bridge_variables
  digi_reboot_report_variables
  dri_bridge_variables
  email_tagger_kre_bridge_variables
  email_tagger_monitor_variables
  hawkeye_affecting_monitor_variables
  hawkeye_bridge_variables
  links_metrics_api_variables
  lumin_billing_report_variables
  notifier_variables
  service_affecting_monitor_variables
  service_outage_monitor_variables
  t7_bridge_variables
  ticket_collector_variables
  velocloud_bridge_variables
}

function main() {
  environments_assign
}

main