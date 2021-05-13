#!/bin/bash

function common_variables_by_environment() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # common variables for ephemeral environments
    export LAST_CONTACT_RECIPIENT=${LAST_CONTACT_RECIPIENT_DEV}
    export KRE_BASE_URL=${KRE_BASE_URL_DEV}
  else
    # common environment variables for production environment
    export LAST_CONTACT_RECIPIENT=${LAST_CONTACT_RECIPIENT_PRO}
    export KRE_BASE_URL=${KRE_BASE_URL_PRO}
  fi
}

function bruin_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # bruin-bridge environment variables for ephemeral environments
    export BRUIN_CLIENT_ID=${BRUIN_CLIENT_ID_PRO}
    export BRUIN_CLIENT_SECRET=${BRUIN_CLIENT_SECRET_PRO}
    export BRUIN_LOGIN_URL_IP="\"\""
    export BRUIN_LOGIN_URL=${BRUIN_LOGIN_URL_PRO}
    export BRUIN_BASE_URL_IP="\"\""
    export BRUIN_BASE_URL=${BRUIN_BASE_URL_PRO}
  else
    # bruin-bridge environment variables for production environment
    export BRUIN_CLIENT_ID=${BRUIN_CLIENT_ID_PRO}
    export BRUIN_CLIENT_SECRET=${BRUIN_CLIENT_SECRET_PRO}
    export BRUIN_LOGIN_URL_IP="\"\""
    export BRUIN_LOGIN_URL=${BRUIN_LOGIN_URL_PRO}
    export BRUIN_BASE_URL_IP="\"\""
    export BRUIN_BASE_URL=${BRUIN_BASE_URL_PRO}
  fi
}

function cts_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # cts-bridge environment variables for ephemeral environments
    export CTS_CLIENT_ID=${CTS_CLIENT_ID_DEV}
    export CTS_CLIENT_SECRET=${CTS_CLIENT_SECRET_DEV}
    export CTS_CLIENT_USERNAME=${CTS_CLIENT_USERNAME_DEV}
    export CTS_CLIENT_PASSWORD=${CTS_CLIENT_PASSWORD_DEV}
    export CTS_CLIENT_SECURITY_TOKEN=${CTS_CLIENT_SECURITY_TOKEN_DEV}
    export CTS_LOGIN_URL=${CTS_LOGIN_URL_DEV}
    export CTS_DOMAIN=${CTS_DOMAIN_DEV}
  else
    # cts-bridge environment variables for production environment
    export CTS_CLIENT_ID=${CTS_CLIENT_ID_PRO}
    export CTS_CLIENT_SECRET=${CTS_CLIENT_SECRET_PRO}
    export CTS_CLIENT_USERNAME=${CTS_CLIENT_USERNAME_PRO}
    export CTS_CLIENT_PASSWORD=${CTS_CLIENT_PASSWORD_PRO}
    export CTS_CLIENT_SECURITY_TOKEN=${CTS_CLIENT_SECURITY_TOKEN_PRO}
    export CTS_LOGIN_URL=${CTS_LOGIN_URL_PRO}
    export CTS_DOMAIN=${CTS_DOMAIN_PRO}
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
    export DIGI_REPORT_RECIPIENT=${DIGI_REPORT_RECIPIENT_DEV}
  else
    # digi-reboot-report environment variables for production environment
    export DIGI_REPORT_RECIPIENT=${DIGI_REPORT_RECIPIENT_PRO}
  fi
}

function email_tagger_monitor_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # email-tagger-monitor environment variables for ephemeral environments
    export REQUEST_SIGNATURE_SECRET_KEY=${REQUEST_SIGNATURE_SECRET_KEY_DEV}
    export REQUEST_API_KEY=${REQUEST_API_KEY_DEV}
    export API_SERVER_ENDPOINT_PREFIX=${API_SERVER_ENDPOINT_PREFIX_DEV}
  else
    # email-tagger-monitor environment variables for production environment
    export REQUEST_SIGNATURE_SECRET_KEY=${REQUEST_SIGNATURE_SECRET_KEY_PRO}
    export REQUEST_API_KEY=${REQUEST_API_KEY_PRO}
    export API_SERVER_ENDPOINT_PREFIX=${API_SERVER_ENDPOINT_PREFIX_PRO}
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

function lit_bridge_variables() {
  if [[ "${CI_COMMIT_REF_SLUG}" != "master" ]]; then
    # lit-bridge environment variables for ephemeral environments
    export LIT_CLIENT_ID=${LIT_CLIENT_ID_DEV}
    export LIT_CLIENT_SECRET=${LIT_CLIENT_SECRET_DEV}
    export LIT_CLIENT_USERNAME=${LIT_CLIENT_USERNAME_DEV}
    export LIT_CLIENT_PASSWORD=${LIT_CLIENT_PASSWORD_DEV}
    export LIT_CLIENT_SECURITY_TOKEN=${LIT_CLIENT_SECURITY_TOKEN_DEV}
    export LIT_LOGIN_URL=${LIT_LOGIN_URL_DEV}
    export LIT_DOMAIN=${LIT_DOMAIN_DEV}
  else
    # lit-bridge environment variables for production environment
    export LIT_CLIENT_ID=${LIT_CLIENT_ID_PRO}
    export LIT_CLIENT_SECRET=${LIT_CLIENT_SECRET_PRO}
    export LIT_CLIENT_USERNAME=${LIT_CLIENT_USERNAME_PRO}
    export LIT_CLIENT_PASSWORD=${LIT_CLIENT_PASSWORD_PRO}
    export LIT_CLIENT_SECURITY_TOKEN=${LIT_CLIENT_SECURITY_TOKEN_PRO}
    export LIT_LOGIN_URL=${LIT_LOGIN_URL_PRO}
    export LIT_DOMAIN=${LIT_DOMAIN_PRO}
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
  cts_bridge_variables
  digi_bridge_variables
  digi_reboot_report_variables
  email_tagger_monitor_variables
  hawkeye_bridge_variables
  lit_bridge_variables
  lumin_billing_report_variables
  notifier_variables
  t7_bridge_variables
  velocloud_bridge_variables
}

function main() {
  environments_assign
}

main