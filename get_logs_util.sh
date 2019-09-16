#!/bin/bash

get_cluster_task_id () {
    task=$(ecs-cli ps --cluster ${CLUSTER_ID} --desired-status RUNNING | grep ${TASK} | awk '{ print $1 }')
    task_id="$( cut -d '/' -f 1 <<< "$task" )"
}

get_cluster_task_id_logs () {
    get_cluster_task_id
    if [ ! -z "$task_id" ]; then
        ecs-cli logs --follow --cluster ${CLUSTER_ID} --task-id ${task_id}
    fi
}

while getopts f:a: option 
do
    case "${option}" in
        c) CLUSTER_ID=${OPTARG};;
        t) TASK=${OPTARG};;
    esac
done

if [ ! -z "$CLUSTER_ID" ] && [ ! -z "$TASK" ]; then
    get_cluster_task_id_logs
fi