#!/bin/bash

source $(dirname "$0")/common_functions.sh

create_grafana_user () {
    grafana_user_creation_result=$(curl --write-out "%{http_code}\n" --silent --output /dev/null \
        -XPOST --user $GRAFANA_ADMIN_USER:$GRAFANA_ADMIN_PASSWORD -H "Content-Type: application/json" -d '{
            "name": "'"$GRAFANA_USER_NAME"'",
            "email": "'"$GRAFANA_USER_EMAIL"'",
            "login": "'"$GRAFANA_USER_LOGIN"'",
            "password":"'"$GRAFANA_USER_PASSWORD"'"
        }' https://admin:admin@$ENVIRONMENT_SLUG.mettel-automation.net/api/admin/users)
    check_grafana_user_creation $grafana_user_creation_result
}

check_grafana_user_creation () {
    if [ -z "$1" ] || [ "$1" != "200" ]; then
        s_err "User $GRAFANA_USER_LOGIN not created in Grafana"
        exit 1
    elif [ ! -z "$1" ] && [ "$1" == "200" ]; then
        s_info "User $GRAFANA_USER_LOGIN successfully created in Grafana"
    fi
}

create_grafana_user
