#!/bin/sh

function s_info() {
    echo "INFO: $1"
}

function s_err() {
    echo "ERROR: $1"
}

function substitute_environment_in_bucket_file() {
    sed -i "s/ENVIRONMENT/${ENVIRONMENT}/g" /tmp/bucket_config.yaml
}

function start_sidecar() {
    if [[ ! -z "${prometheus_tsdb_path}" && ! -z "${prometheus_HTTP_PORT}" \
        && ! -z "${thanos_sidecar_objstore_config_file}" && ! -z "${thanos_sidecar_GRPC_PORT}" \
        && ! -z "${thanos_sidecar_HTTP_PORT}" ]]; then
        s_info "Starting sidecar thanos component"
        /bin/thanos sidecar --tsdb.path=${prometheus_tsdb_path} \
        --prometheus.url=http://localhost:${prometheus_HTTP_PORT} \
        --objstore.config-file=${thanos_sidecar_objstore_config_file} \
        --grpc-address=localhost:${thanos_sidecar_GRPC_PORT} \
        --http-address=localhost:${thanos_sidecar_HTTP_PORT}
    else
        s_err "It's necessary provide prometheus_tsdb_path, prometheus_HTTP_PORT, \
               thanos_sidecar_objstore_config_file, thanos_sidecar_GRPC_PORT and thanos_sidecar_HTTP_PORT"
    fi
}

function start_store_gateway() {
    if [[ ! -z "${thanos_store_gateway_objstore_config_file}" && ! -z "${thanos_store_gateway_HTTP_PORT}" \
            && ! -z "${thanos_store_gateway_GRPC_PORT}" ]]; then
        s_info "Starting store gateway thanos component"
        /bin/thanos store --data-dir=/thanos/store \
        --objstore.config-file=${thanos_store_gateway_objstore_config_file} \
        --http-address=localhost:${thanos_store_gateway_HTTP_PORT} \
        --grpc-address=localhost:${thanos_store_gateway_GRPC_PORT}
    else
        s_err "It's necessary provide thanos_store_gateway_objstore_config_file, \
               thanos_store_gateway_HTTP_PORT and thanos_store_gateway_GRPC_PORT"
    fi
}

function check_conditions_thanos() {
    if [[ -z "${THANOS_COMPONENT}" ]]; then
        s_err "It's necessary provide THANOS_COMPONENT as environment variable"
        exit 1
    elif [[ "$THANOS_COMPONENT" == "sidecar" ]]; then
        start_sidecar
    elif [[ "$THANOS_COMPONENT" == "store-gateway" ]]; then
        start_store_gateway
    else
        s_err "THANOS_COMPONENT not recognized, the only options available are sidecar or store-gateway"
    fi
}

function start() {
    substitute_environment_in_bucket_file
    check_conditions_thanos
}

start