#!/bin/bash

# python3 /metrics-dashboard/grafana/app.py

rm -rf /metrics-dashboard/dashboards
rm -rf /metrics-dashboard/dashboards-definitions

(python3 /metrics-dashboard/grafana/grafana_users_creation.py)&

/run.sh