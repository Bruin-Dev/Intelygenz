#!/bin/bash

python3 /metrics-dashboard/grafana/app.py

rm -rf /metrics-dashboard
rm -rf /custompackages
#rm -rf /var/lib/grafana/dashboards/dummy/

/run.sh