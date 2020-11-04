# Table of contents
- [Hawkeye API](#hawkeye-api)
  - [Description](#description)
  - [Links](#links)
- [Running in docker-compose](#running-in-docker-compose)

# Hawkeye API

## Description
Hawkeye Bridge is used to make calls to the Hawkeye API.

## Links
Hawkeye swagger:
https://ixia.metconnect.net/swagger/index.html

Hawkeye app:
https://ixia.metconnect.net/ixrr_login.php

# Running in docker-compose 
`docker-compose up --build redis nats-server hawkeye-bridge`