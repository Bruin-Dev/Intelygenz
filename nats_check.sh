#!/bin/sh

i=1
while [ $i -le 30 ]
do
    sleep 5
    i=$(( $i + 1 ))
    nats_status=`ecs-cli ps --cluster $TF_VAR_ENVIRONMENT --desired-status RUNNING | grep "nats" | awk '{ print $6 }'`
    if [ $nats_status = "HEALTHY" ]; then
        echo "$i: NATS server is ready"
        break
    else
        echo "$i: NATS server is not ready yet"
    fi
done
