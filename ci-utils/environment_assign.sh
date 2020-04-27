#!/bin/bash

if [[ ${CI_COMMIT_REF_SLUG} == "master" ]]; then
    export ENVIRONMENT_VAR="automation-master"
    export DNS_ENVIRONMENT_VAR="https://master.mettel-automation.net"
else
    ENVIRONMENT_ID=$(echo -n "${CI_COMMIT_REF_SLUG}" | sha256sum | cut -c1-8)
    export ENVIRONMENT_VAR="automation-"${ENVIRONMENT_ID}
    export DNS_ENVIRONMENT_VAR="https://"${ENVIRONMENT_ID}".mettel-automation.net"
fi