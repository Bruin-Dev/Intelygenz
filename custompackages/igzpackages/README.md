# Packages
## event-bus
### event_bus (class)
The event bus is the entity responsible for the management of subscriptions and the addition of consumers and the corresponding
producer in each microservice. This is the piece between NATS and producers/consumers as it also is in charge of creating and
destroying the connections of these entities with the NATS server.

It also forwards messages published (either via `publish()` or `rpc_request()`) to the proper `NATSClient` instance.
If the message is larger than 1MB, it will be stored within an external storage service as NATS is not able to forward
such kind of messages.

Every single consumer (a `NATSClient` instace), when registered through the event bus, is patched in runtime in order to make the callback
registered to _react_ to an event (i.e., a message published to a topic that the consumer is subscribed to) capable to recover
messages larger than 1MB that were stored into an external storage service (see [storage_managers](#storage_managers) section).

This artifact acts as a singleton at microservice level; that is, there should be just one event bus per microservice. Developers
should use it to manage `NATSClient` instances instead of using these instances directly.

### storage_managers
Storage managers are artifacts that allow storing and retrieving messages by using an external storage service. It is an abstraction
specified by the abstract base class `MessageStorageManager` that can be subclassed to support additional storage services. To subclass
it, both `store_message()` and `recover_message()` methods must be implemented.

These pieces are intended to be injected into `EventBus` instances. The idea behind this artifact is that messages stored with
`store_message()` should be easily recoverable with `recover_message()`.

At the time of this writing, **Redis** is the only external storage service supported (through the concrete class `RedisStorageManager`).

#### Redis storage manager
When a message is published through the `EventBus::publish()` or `EventBus::rpc_request()` methods, it is previously stored into Redis
with `store_message()` and a message with the following structure is delivered instead:
```
{
    "token": "jUh2DjpY8Mke3evRtdqFej",  # This is just an UUID
    "is_stored": true
}
```

In case it needs to be recovered from Redis, the message above is passed to `receive_message()` and then the original message is finally
recovered.

## nats
### clients
This is a wrapper of the official [NATS client for python](https://github.com/nats-io/asyncio-nats)
It expects to receive a config object that has something like [this one](../../base-microservice/src/config/config.py) with a NATS_CONFIG dictionary
There are a lot of possible configurations due different scenarios. 
All non-critical parameters for a base configuration are set to a default.

This object accepts multiple subscriptions. 

The callback passed in the `subscribe` will be called with the decoded JSON that represents an event.

## quart
### api
`Quart` is an async version of `Flask`. Its used to check the status of the microservice its 
attached to. By making a `Get` call when the microservices' address are up should return `null` and a 
status code of `200`. 

`QuartServer` is a class that builds the `Quart` app, and set up the configs for the `Hypercorn` server. It
also contains the class `HealthCheck` which handles the calls made to the `Quart` app.

`Hypercorn` is used to run the quart app. `Hypercorn` has a config file and within in it
is a variable `bind`. `bind` is formatted to be IP address:Port. Default is `"127.0.0.1:8000"`.
For our version we must change the bind to be `0.0.0.0:{self._port}`. With `self.port` being a port
taken from the configs of the microservice that defines the `QuartServer` class.
 
`HealthCheck` is the results of using `quart-open-api`. Which is an extension of `Quart` and the quart 
equivalent to `flask-RESTful` we can recieve a status code of `200` or `OK` whenever a `GET` call it made to the
`Hypercorn` server.

__Microservices' healthcheck endpoints (for local enviroments)__

sites-monitor: `http://localhost:5000/_health` 

velocloud-bridge: `http://localhost:5001/_health`

notifier:  `http://localhost:5002/_health`
