**Table of contents**

- [Forticloud Poller](#forticloud-poller)
  - [Description](#forticloud-poller-description)
- [Running in docker-compose](#running-in-docker-compose)

# Forticloud poller

## Description <a name="forticloud-poller-description"></a>

The forticloud poller get forticloud devices data from forticloud cache and send it through nats

## 

### Description <a name="_description"></a>

# Running in docker-compose

`docker-compose up --build redis nats-server forticloud-poller`
