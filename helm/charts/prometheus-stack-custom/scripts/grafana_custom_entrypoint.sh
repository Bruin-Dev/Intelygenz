#!/bin/bash

echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/main' >> /etc/apk/repositories
apk update && apk add python3=3.6.9-r3
python3 --version