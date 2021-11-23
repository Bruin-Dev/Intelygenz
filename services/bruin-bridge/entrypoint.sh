#!/bin/sh

if [ "$CURRENT_ENVIRONMENT" = "dev" ]; then
  echo "" >> /etc/hosts
  echo "${DEV__BRUIN_BRIDGE__BRUIN_LOGIN_URL_IP} ${DEV__BRUIN_BRIDGE__BRUIN_LOGIN_URL#https://}" >> /etc/hosts
  echo "${DEV__BRUIN_BRIDGE__BRUIN_BASE_URL_IP} ${DEV__BRUIN_BRIDGE__BRUIN_BASE_URL#https://}" >> /etc/hosts
fi

python3 -u src/app.py