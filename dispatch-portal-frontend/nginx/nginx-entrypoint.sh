#!/bin/bash

envsubst '${CURRENT_ENVIRONMENT} ${ENVIRONMENT} ${PAPERTRAIL_HOST} ${PAPERTRAIL_PORT} ${BUILD_NUMBER} ${ENVIRONMENT_NAME}'< /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/nginx.conf
exec "$@"
