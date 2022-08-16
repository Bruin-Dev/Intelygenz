# Table of contents
- [Forticloud integration](#forticloud-integration)
  * [Connecting to several clusters](#connecting-to-several-clusters)
  * [Service logic](#service-logic)

# Forticloud integration

## Connecting to several clusters
Forticloud provided us with endpoints to make request calls to. The client that makes the request calls is located 
in the `client` folder of the `forticloud-bridge`.

The service's Forticloud client will create a client in a list for each host the service must connect to.

Credentials are put inside an environment variable with the next schema:
`some.host.name+hostusername+hostpassword;other.host.name+otherusername+otherpassword`

In the `config.py`script, there's a way to split this into an array of dictionaries like this one:

````
        {'url': "some.host.name",
         'username': "hostusername",
         'password': "hostpassword"
         }
````

## Service logic
TODO