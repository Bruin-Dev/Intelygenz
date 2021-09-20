#!/bin/bash

function s_info() {
    echo "INFO: $1"
}

function s_err() {
    echo "ERROR: $1"
}

function create_nats_cluster_seed() {
    if [[ ! -z "${PORT}" && ! -z "${NATSCLUSTER}" ]]; then
        s_info "Starting NATS in cluster mode seed server using port $PORT and cluster URL ${NATSCLUSTER}"
        nats-server -p "$PORT" -cluster "$NATSCLUSTER" -m 8222 -D
    else
        s_err "It's necessary provide PORT and NATSCLUSTER environment variables"
        exit 1
    fi
}

function create_nats_cluster_not_seed() {
    if [[ ! -z "${PORT}" && ! -z "${NATSCLUSTER}" && ! -z "${NATSROUTECLUSTER}" ]]; then
        s_info "Starting NATS in cluster mode using port ${PORT}, cluster URL ${NATSCLUSTER} and route url ${NATSROUTECLUSTER}"
        nats-server -p "$PORT" -cluster "$NATSCLUSTER" -routes "${NATSROUTECLUSTER}" -m 8222 -D
    else
        s_err "It's necessary provide PORT, NATSCLUSTER and NATSROUTECLUSTER environment variables"
    fi
}

check_conditions_nats_cluster() {
    if [[ -z "${CLUSTER_MODE}" ]]; then
        s_err "It's necessary provide CLUSTER_MODE as environment variable"
        exit 1
    elif [[ "$CLUSTER_MODE" == "s" ]]; then
        create_nats_cluster_seed
    elif [[ "$CLUSTER_MODE" == "n" ]]; then
        create_nats_cluster_not_seed
    else
        s_err "Option not recognized, the only options available are s (specifying seed node) and n (without specifying seed node)"
    fi
}

check_conditions_nats_cluster
