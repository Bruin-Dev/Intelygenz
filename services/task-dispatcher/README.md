# Table of contents
  * [Description](#description)
  * [Overview](#overview)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The `task-dispatcher` service is in charge of getting due tasks and executing them at the appropriate time.

  Supported tasks are:

  * Forward ticket tasks to Bruin work queues

# Overview
This service was created with the aim of circumvent a problem we were facing with losing tasks when a service was restarted. This service keeps track of all tasks until they are done.

# Capabilities used
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifications bridge](../notifications-bridge/README.md)

# Running in docker-compose
`docker-compose up --build nats-server redis bruin-bridge notifications-bridge`
