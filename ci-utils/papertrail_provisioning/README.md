# Papertrail provisioning

In this folder are the utilities to perform the papertrail provisioning for the different microservices of the project in each environment.

### Usage  <a name="papertrail_provisioning_usage"></a>

This utility is intended to be used in the gitlab deployment pipelines for each environment, it uses a configuration file called [config.py](./config.py) where it will collect the different environment variables needed.

It is possible to add and/or remove papertrail groups, as well as the searches on them by means of the mentioned config.py file, through the modification of the dictionary value named PAPERTRAIL_PROVISIONING.
