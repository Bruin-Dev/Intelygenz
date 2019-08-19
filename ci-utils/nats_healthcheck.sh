#!/bin/bash

source $(dirname "$0")/common_functions.sh

get_nats_tasks_major_number () {
    nats_server_running_tasks=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $5 }'`
    if [ -z "$nats_server_running_tasks" ]; then
        s_err "No NATS cluster task exists"
        exit 1
    else
        s_info "NATS Server Running tasks are the following"
        iterate_over_lines $nats_server_running_tasks
    fi
    nats_task_major=`echo "${nats_server_running_tasks[*]}" | sort -nr | head -n1`
    s_info "NATS Server Running task with major identifier is $nats_task_major"
}

wait_nats_server_healthy () {
    i=1
    while [ $i -le 10 ]
    do
        sleep 30
        if [ $i -eq 1 ]; then
            get_nats_tasks_major_number
        fi
        nats_task=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep $nats_task_major`
        s_info "Try $i. Waiting for the task with task definition $nats_task_major to be in HEALTHY state"
        nats_status=`echo $nats_task | awk '{ print $6 }'`
        s_info "Try $i. Health Status of NATS task is $nats_status"
        if [ ! -z "$nats_status" ] && [ $nats_status = "HEALTHY" ]; then
            s_info "Try $i. NATS Server task is ready"
            break
        else
            s_info "Try $i. NATS Server task is not ready yet"
        fi
        i=$(( $i + 1 ))
    done
}

nats_server_healthcheck () {
    wait_nats_server_healthy
    if [ $i -ge 10 ]; then
        s_err "NATS Server task $nats_task_major hasn't reached HEALTHY state in 5 minutes. Aborting job"
        exit 1
    fi
}

nats_server_healthcheck