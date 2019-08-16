#!/bin/sh

i=1
while [ $i -le 30 ]
do
    sleep 10
    nats_task=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats"`
    echo "$i: nats_task is $nats_task"
    nats_status=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $6 }'`
    echo "nats_status is $nats_status"
    if [ ! -z "$nats_status" ] && [[ $nats_status = "HEALTHY" ]]; then
        echo "$i: NATS server is ready"
        break
    else
        echo "$i: NATS server is not ready yet"
    fi
    i=$(( $i + 1 ))
done
