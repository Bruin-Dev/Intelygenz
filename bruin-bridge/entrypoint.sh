#!/bin/sh

if [ "$CURRENT_ENVIRONMENT" = "dev" ]; then
  echo "${BRUIN_LOGIN_URL_IP} ${BRUIN_LOGIN_URL#https://}" >> /etc/hosts
  echo "${BRUIN_BASE_URL_IP} ${BRUIN_BASE_URL#https://}" >> /etc/hosts
fi

python3 -u src/app.py