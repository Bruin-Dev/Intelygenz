#!/bin/sh

get_nats_tasks_numbers () {
    nats_server_running_tasks=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $5 }'`
    echo "nats_server_running_tasks are $nats_server_running_tasks"
    for word in $nats_server_running_tasks; do
        echo "word is $word"
        A=`echo $word | cut -d':' -f2`
        echo "A is $A"
        if [ -z "$n_task_1" ]; then
            n_task_1=$word
        elif [ -z "$n_task_2" ]; then
            n_task_2=$word
        fi
    done
}

get_major_nats_task_number () {
    if [ ! -z $n_task_1 ] && [ ! -z $n_task_2 ]; then
        if [ $n_task_1 -gt $n_task_2 ]; then
            n_task_nats_server=$n_task_1
        elif [ $n_task_2 -gt $n_task_2]; then
            n_task_nats_server=$n_task_2
        fi
    elif [ ! -z $n_task_1 ]; then
        n_task_nats_server=$n_task_1
    elif [ ! -z $n_task_2 ]; then
        n_task_nats_server=$n_task_2
    fi
    echo "n_task_nats_server is $n_task_nats_server"
}

i=1
while [ $i -le 30 ]
do
    sleep 10
    get_nats_tasks_numbers
    get_major_nats_task_number
    nats_task=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | grep $n_task_nats_server`
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
