#!/bin/bash

get_nats_tasks_major_number () {
    nats_server_running_tasks=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $5 }'`
    echo "nats_server_running_tasks are $nats_server_running_tasks"
    nats_task_major=`echo "${nats_server_running_tasks[*]}" | sort -nr | head -n1`
    echo "nats_task_major is $nats_task_major"
}

nats_server_healthcheck () {
    i=1
    while [ $i -le 10 ]
    do
        sleep 30
        if [ $i -eq 1 ]; then
            get_nats_tasks_major_number
        fi
        nats_task=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | grep $nats_task_major`
        echo "$i: nats_task is $nats_task"
        nats_status=`echo $nats_task | awk '{ print $6 }'`
        echo "$i: nats_status is $nats_status"
        if [ ! -z "$nats_status" ] && [ $nats_status = "HEALTHY" ]; then
            echo "$i: NATS server is ready"
            break
        else
            echo "$i: NATS server is not ready yet"
        fi
        i=$(( $i + 1 ))
    done
}

nats_server_healthcheck