#!/bin/bash

function delete_innecessary_lines() {
    if [[ -z "${RUN_MODE}" ]] || [[ "$RUN_MODE" != "local" ]]; then
        echo "Deleting RESOLVER_DISPATCH_PORTAL"
        sed -i '/${RESOLVER_DISPATCH_PORTAL}/d' /etc/nginx/conf.d/nginx.conf.template
    fi
}

function assign_necessary_variables() {
    if [[ "$RUN_MODE" == "local" ]]; then
        export RESOLVER_DISPATCH_PORTAL_API="127.0.0.11"
        export PROXY_PASS_DISPATCH_PORTAL_API="http://dispatch-portal-backend:5000/"
        export RESOLVER_DISPATCH_PORTAL="127.0.0.11"
        export PROXY_PASS_DISPATCH_PORTAL="http://dispatch-portal-frontend:3000/"
    else
        export RESOLVER_DISPATCH_PORTAL_API="169.254.169.253"
        export PROXY_PASS_DISPATCH_PORTAL_API="http://dispatch-portal-backend-${ENVIRONMENT}.${ENVIRONMENT}.local:5000/"
        export PROXY_PASS_DISPATCH_PORTAL="http://localhost:3000/"
    fi
}

function assign_vars_to_nginx_conf() {
    if [[ -z "${RUN_MODE}" ]] || [[ "$RUN_MODE" != "local" ]]; then
        envsubst '${RESOLVER_DISPATCH_PORTAL_API} ${PROXY_PASS_DISPATCH_PORTAL_API} ${PROXY_PASS_DISPATCH_PORTAL} ${CURRENT_ENVIRONMENT} ${PAPERTRAIL_HOST} ${PAPERTRAIL_PORT} ${BUILD_NUMBER} ${ENVIRONMENT_NAME}'< /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/nginx.conf
    elif [[ "$RUN_MODE" == "local" ]]; then
        envsubst '${RESOLVER_DISPATCH_PORTAL_API} ${PROXY_PASS_DISPATCH_PORTAL_API} ${RESOLVER_DISPATCH_PORTAL} ${PROXY_PASS_DISPATCH_PORTAL} ${CURRENT_ENVIRONMENT} ${PAPERTRAIL_HOST} ${PAPERTRAIL_PORT} ${BUILD_NUMBER} ${ENVIRONMENT_NAME}'< /etc/nginx/conf.d/nginx.conf.template > /etc/nginx/nginx.conf
    fi
}

function configure_nginx () {
    delete_innecessary_lines
    assign_necessary_variables
    assign_vars_to_nginx_conf
}

configure_nginx
exec "$@"