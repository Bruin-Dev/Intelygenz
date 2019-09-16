#!/bin/bash

/bin/bash /run.sh

curl -v -XPOST "-H Content-Type: application/json" -d '{\"name\":\"User\", \"email\":\"user@graf.com\", \"login\":\"user\", \"password\":\"userpassword\"}' http://admin:${GF_SECURITY_ADMIN_PASSWORD}@localhost:3000/api/admin/users