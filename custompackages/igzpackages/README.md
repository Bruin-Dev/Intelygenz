#Packages
## nats
### clients
This is a wrapper of the official [nats streaming client for python](https://github.com/nats-io/asyncio-nats-streaming)
It expects to recieve a config object that has something like [this one](../../base-microservice/src/config/config.py) with a NATS_CONFIG dictionary
There are a lot of possible configurations due different scenarios. 
All non-critical parameters for a base configuration are set to a default.

The parameters `start_at` and `durable_name` are quite important.
- `start_at= 'first'` will consume the full queue, despite of ack status of the messages.
- `start_at= 'new_only'` will only consume the no-ack messages in the queue.
- `durable_name` is used to keep the track of the consumed messages for a clientID. Clients with durable names that reconnect to NATS should continue their subscription drain in the point they left.

This object accepts multiple subscriptions. 

The callback passed in the `subscribe` will be called with the decoded JSON that represents an event.
If the callback fails, the message wont be ACKed.
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

velocloud-orchestrator: `http://0.0.0.0:5000/_health` or `http://localhost:5000/_health`

velocloud-bridge: `http://localhost:5001/_health`

velocloud-notificator:  `http://localhost:5002/_health`
