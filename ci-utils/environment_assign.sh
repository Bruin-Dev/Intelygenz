#!/bin/bash
if [[ ${CI_COMMIT_REF_SLUG} == "master" ]]; then
    export ENVIRONMENT_VAR="master"
else
    export ENVIRONMENT_VAR=$(echo -n "${CI_COMMIT_REF_SLUG}" | sha256sum | cut -c1-8)
fi