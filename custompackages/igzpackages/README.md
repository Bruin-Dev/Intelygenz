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