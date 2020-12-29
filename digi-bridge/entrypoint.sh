#!/bin/sh

if [ "$CURRENT_ENVIRONMENT" = "production" ]; then
  echo "${DIGI_IP_PRO} ${DIGI_RECORD_NAME_PRO}" >> /etc/hosts
else
  echo "${DIGI_IP_DEV} ${DIGI_RECORD_NAME_DEV}" >> /etc/hosts
  echo "${DIGI_IP_TEST} ${DIGI_RECORD_NAME_TEST}" >> /etc/hosts
fi

python3 -u src/app.py