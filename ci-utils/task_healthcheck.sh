#!/bin/bash

source $(dirname "$0")/common_functions.sh

task_major_number () {
    if [[ ${TASK} == *prometheus* ]] || [[ ${TASK} == *grafana* ]] || [[ ${TASK} == *notifier* ]]; then
        tasks_running=$(ecs-cli ps --cluster ${TF_VAR_ENVIRONMENT} --desired-status RUNNING | grep ${TASK} | awk '{ print $4 }')
    elif [[ ${TASK} == *nats-server* ]]; then
         tasks_running=$(ecs-cli ps --cluster ${TF_VAR_ENVIRONMENT} --desired-status RUNNING | grep nats-server | grep -v nats-server- | awk '{ print $6 }')
    else
        tasks_running=$(ecs-cli ps --cluster ${TF_VAR_ENVIRONMENT} --desired-status RUNNING | grep ${TASK} | awk '{ print $5 }')
    fi
    if [[ -z "$tasks_running" ]]; then
        s_err "No $TASK task exists"
        exit 1
    else
        s_info "$TASK Running tasks are the following"
        iterate_over_lines ${tasks_running}
    fi
    task_running_major=$(echo "${tasks_running[*]}" | sort -nr | head -n1)
    s_info "$TASK Running task with major identifier is $task_running_major"
}

wait_task_healthy () {
    i=1
    while [[ ${i} -le 10 ]]
    do
        sleep 30
        if [[ ${i} -eq 1 ]]; then
            task_major_number
        fi
        selected_task=$(ecs-cli ps --cluster ${TF_VAR_ENVIRONMENT} --desired-status RUNNING | grep ${task_running_major})
        s_info "Try $i. Waiting for the task with task definition $task_running_major to be in HEALTHY state"
        if [[ ${TASK} == *prometheus* ]] || [[ ${TASK} == *grafana* ]] || [[ ${TASK} == *notifier* ]]; then
            task_status=$(echo ${selected_task} | awk '{ print $5 }')
        elif [[ ${TASK} == *nats-server* ]]; then
            task_status=$(echo ${selected_task} | awk '{ print $7 }')
        else 
            task_status=$(echo ${selected_task} | awk '{ print $6 }')
        fi
        s_info "Try $i. Health Status of $TASK task is $task_status"
        if [[ ! -z "$task_status" ]] && [[ ${task_status} = "HEALTHY" ]]; then
            s_info "Try $i. $TASK task is ready"
            break
        else
            s_info "Try $i. $TASK task is not ready yet"
        fi
        i=$(( $i + 1 ))
    done
}

task_healthcheck () {
    wait_task_healthy
    if [[ ${i} -ge 10 ]]; then
        s_err "$TASK task $task_running_major hasn't reached HEALTHY state in 5 minutes. Aborting job"
        exit 1
    fi
}

while getopts t: option 
do
    case "${option}" in
        t) TASK=${OPTARG};;
    esac
done

task_healthcheck