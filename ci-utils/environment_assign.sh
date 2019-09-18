#!/bin/bash
if [[ ${CI_COMMIT_REF_SLUG} == "master" ]]; then
    export ENVIRONMENT_SLUG=master
else
    export ENVIRONMENT_SLUG=$(echo -n "${CI_COMMIT_REF_SLUG}" | sha256sum | cut -c1-8)
fi