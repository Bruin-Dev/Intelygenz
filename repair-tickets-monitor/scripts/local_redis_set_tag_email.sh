#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))
EMAIL_ID="1234_test"

source $SCRIPT_PATH/../src/config/env

redis-cli -p 6382 -x set $ENVIRONMENT_NAME-tag_email_$EMAIL_ID < $SCRIPT_PATH/assets/email_sample.json
