#!/bin/sh

nats_server_running_tasks=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $6 }'`
echo "nats_server_running_tasks are $nats_server_running_tasks"
for word in $nats_server_running_tasks; do
    A="$(cut -d':' -f2 <<<$word)"
    if [ -z "$n_task_1" ]; then
        n_task_1=$A
    elif [ -z "$n_task_2" ]; then
        n_task_2=$A
    fi
done
if [ $n_task_1 -gt $n_task_2 ]; then
    n_task_nats_server=$n_task_1
elif [ $n_task_2 -gt $n_task_2]; then
    n_task_nats_server=$n_task_2
fi
echo "n_task_nats_server is $n_task_nats_server"

i=1
while [ $i -le 30 ]
do
    sleep 10
    nats_task=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | grep $n_task_nats_server`
    echo "$i: nats_task is $nats_task"
    nats_status=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $6 }' | grep $n_task_nats_server`
    echo "$i: nats_status is $nats_status"
    if [ ! -z "$nats_status" ] && [ "$nats_status" == "HEALTHY" ]; then
        echo "$i: NATS server is ready"
        break
    else
        echo "$i: NATS server is not ready yet"
    fi
    i=$(( $i + 1 ))
done
