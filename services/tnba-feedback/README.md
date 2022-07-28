# Table of contents
  * [Description](#description)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
Every hour the `tnba-feedback` service will collect all the closed tickets from the past
day. Then it will check the task history of all those tickets and see if there is a TNBA note inside
the task history. If it is then it will send that ticket's task history to T7.

# Capabilities used
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifications bridge](../notifications-bridge/README.md)
- [T7 bridge](../t7-bridge/README.md)

# Running in docker-compose
1. Turn VPN on
2. `docker-compose up --build redis nats-server t7-bridge notifications-bridge`
3. Run bruin in pycharm 
4. `docker-compose up --build tnba-feedback`
