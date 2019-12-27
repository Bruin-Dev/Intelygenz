#!/usr/bin/bash

sleep 200
curl -kv http://prometheus-automation-92a00834.automation-92a00834.local:19091
nc -zv prometheus-automation-92a00834.automation-92a00834.local 19091
curl -kv http://prometheus-automation-92a00834.automation-92a00834.local:9090
nc -zv prometheus-automation-92a00834.automation-92a00834.local 9090