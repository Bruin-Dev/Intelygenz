# Table of contents
 

# DiGi API
### Description

# Running in docker-compose 
`docker-compose up --build redis nats-server digi-bridge`

# Entrypoint note
Since Mettel won't expose their DNS server, we need to modify the /etc/hosts file to contain the domain name translation.
That's why, instead of executing app.py as the rest of the services, this service has a `entrypoint.sh`
script which first will modify the /etc/hosts file and then will launch with python the `app.py` file.