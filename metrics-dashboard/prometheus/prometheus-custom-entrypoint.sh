#!/bin/sh

function substitute_environment_in_config() {
    sed -i "s/ENVIRONMENT/${ENVIRONMENT}/g" /etc/prometheus/prometheus.yml
}


function start() {
    substitute_environment_in_config
    /bin/prometheus --config.file /etc/prometheus/prometheus.yml \
        --storage.tsdb.path=${prometheus_storage_container_path} \
        --storage.tsdb.retention.time=${prometheus_tsdb_retention_time} \
        --storage.tsdb.min-block-duration=${prometheus_tsdb_block_duration} \
        --storage.tsdb.max-block-duration=${prometheus_tsdb_block_duration}
}

start