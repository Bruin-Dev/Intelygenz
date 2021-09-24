#!/bin/bash

SCRIPT_PATH=$(dirname $(realpath -s $0))
RANDOM_KEY=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 13)

source $SCRIPT_PATH/../src/config/env

redis-cli -p 6382 -x set $ENVIRONMENT_NAME-tag_email_$RANDOM_KEY < $SCRIPT_PATH/assets/email_sample.json
