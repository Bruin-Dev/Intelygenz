#!/bin/bash

function common_variables_by_environment() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # common variables for ephemeral environments
    export LAST_CONTACT_RECIPIENT=${LAST_CONTACT_RECIPIENT_DEV}
    export KRE_TNBA_BASE_URL=${KRE_TNBA_BASE_URL_DEV}
    export KRE_EMAIL_TAGGER_BASE_URL=${KRE_EMAIL_TAGGER_BASE_URL_DEV}
    export KRE_REPAIR_TICKETS_BASE_URL=${KRE_REPAIR_TICKETS_BASE_URL_DEV}
    export BRUIN_CLIENT_ID=${BRUIN_CLIENT_ID_PRO}
    export BRUIN_CLIENT_SECRET=${BRUIN_CLIENT_SECRET_PRO}
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
    export KRE_EMAIL_TAGGER_BASE_URL=${KRE_EMAIL_TAGGER_BASE_URL_PRO}
    export KRE_REPAIR_TICKETS_BASE_URL=${KRE_REPAIR_TICKETS_BASE_URL_PRO}
    export BRUIN_CLIENT_ID=${BRUIN_CLIENT_ID_PRO}
    export BRUIN_CLIENT_SECRET=${BRUIN_CLIENT_SECRET_PRO}
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
    export BRUIN_LOGIN_URL_IP="\"\""
    export BRUIN_LOGIN_URL=${BRUIN_LOGIN_URL_PRO}
    export BRUIN_BASE_URL_IP="\"\""
    export BRUIN_BASE_URL=${BRUIN_BASE_URL_PRO}
  else
    # bruin-bridge environment variables for production environment
    export BRUIN_LOGIN_URL_IP="\"\""
    export BRUIN_LOGIN_URL=${BRUIN_LOGIN_URL_PRO}
    export BRUIN_BASE_URL_IP="\"\""
    export BRUIN_BASE_URL=${BRUIN_BASE_URL_PRO}
  fi
}

function digi_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # digi-bridge environment variables for ephemeral environments
    export DIGI_IP_DEV=${DIGI_IP_DEV}
    export DIGI_RECORD_NAME_DEV=${DIGI_RECORD_NAME_DEV}
    export DIGI_IP_TEST=${DIGI_IP_TEST}
    export DIGI_RECORD_NAME_TEST=${DIGI_RECORD_NAME_TEST}
    export DIGI_CLIENT_ID=${DIGI_CLIENT_ID_DEV}
    export DIGI_CLIENT_SECRET=${DIGI_CLIENT_SECRET_DEV}
    export DIGI_BASE_URL=${DIGI_BASE_URL_DEV}
  else
    # digi-bridge environment variables for production environment
    export DIGI_IP_PRO=${DIGI_IP_PRO}
    export DIGI_RECORD_NAME_PRO=${DIGI_RECORD_NAME_PRO}
    export DIGI_CLIENT_ID=${DIGI_CLIENT_ID_PRO}
    export DIGI_CLIENT_SECRET=${DIGI_CLIENT_SECRET_PRO}
    export DIGI_BASE_URL=${DIGI_BASE_URL_PRO}
  fi
}

function digi_reboot_report_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # digi-reboot-report environment variables for ephemeral environments
    export DIGI_REPORT_RECIPIENT=${LAST_CONTACT_RECIPIENT_DEV}
  else
    # digi-reboot-report environment variables for production environment
    export DIGI_REPORT_RECIPIENT=${LAST_CONTACT_RECIPIENT_PRO}
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

function email_tagger_monitor_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # email-tagger-monitor environment variables for ephemeral environments
    export REQUEST_SIGNATURE_SECRET_KEY=${EMAIL_TAGGER_MONITOR_REQUEST_SIGNATURE_SECRET_KEY_DEV}
    export REQUEST_API_KEY=${EMAIL_TAGGER_KRE_BRIDGE_KRE_BASE_URL_DEV}
  else
    # email-tagger-monitor environment variables for production environment
    export REQUEST_SIGNATURE_SECRET_KEY=${EMAIL_TAGGER_MONITOR_REQUEST_SIGNATURE_SECRET_KEY_PRO}
    export REQUEST_API_KEY=${EMAIL_TAGGER_KRE_BRIDGE_KRE_BASE_URL_PRO}
  fi
}

function hawkeye_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # hawkeye-bridge environment variables for ephemeral environments
    export HAWKEYE_CLIENT_USERNAME=${HAWKEYE_CLIENT_USERNAME_DEV}
    export HAWKEYE_CLIENT_PASSWORD_ENC=${HAWKEYE_CLIENT_PASSWORD_DEV}
    export HAWKEYE_BASE_URL=${HAWKEYE_BASE_URL_DEV}
  else
    # hawkeye-bridge environment variables for production environment
    export HAWKEYE_CLIENT_USERNAME=${HAWKEYE_CLIENT_USERNAME_PRO}
    export HAWKEYE_CLIENT_PASSWORD_ENC=${HAWKEYE_CLIENT_PASSWORD_PRO}
    export HAWKEYE_BASE_URL=${HAWKEYE_BASE_URL_PRO}
  fi
  export HAWKEYE_CLIENT_PASSWORD=$(base64 -d <<< "${HAWKEYE_CLIENT_PASSWORD_ENC}")
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
    export VELOCLOUD_CREDENTIALS=${VELOCLOUD_CREDENTIALS_PRO}
  else
    # velocloud-bridge environment variables for production environment
    export VELOCLOUD_CREDENTIALS=${VELOCLOUD_CREDENTIALS_PRO}
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
  digi_bridge_variables
  digi_reboot_report_variables
  dri_bridge_variables
  email_tagger_monitor_variables
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