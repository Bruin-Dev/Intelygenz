# Table of contents
  - [Service logic](#service-logic)
  - [Get customers](#get-customers)
      * [Description](#description)
      * [Request message](#request-message)
      * [Response message](#response-message)
# Service logic
This service will ask hawkeye-bridge for all the devices across in Hawkeye.

Once it has all Hawkeye devices it will discard any device with no serial.

After that it will use the serial number to get the client ID from Bruin (bruin-bridge). 
It will ask for the management status of that device under that client ID.

If the management status is one of the following: 
"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"
the device will be considered active and added to a temporal map.

When all the devices in Hawkeye are processed it will store that map in Redis under the key `hawkeye`, so it's not lost between executions.

On start and each 4 hours, the process should be executed again to refresh the cache, but the substitution will only be 
done when process is finished and the length of the new cache is greater than 0 elements.

# Get Customers
### Description
When the customer cache receives a request from topic `hawkeye.customer.cache.get` it makes a callback to function get_customers.
If the request message is in the correct format then it should grab the cache from the storage_repository.

There's one filter that can be requested to be applied through the rpc_request: `last_contact_filter`. This filter, if the value is not `None`,
essentially would check the last moment a device was updated / contacted, which can be determined by picking the most recent moment between
`nodetonode.lastUpdate` and `realservice.lastUpdate`, and filter out any devices with such moment before the `last_contact_filter` time specified
in the RPC's payload.

If the cache is empty then the `body` for the response message will send a message indicating that no devices were found for
the specified filters. In case that the cache is still being built, a message informing about that will be sent.

And with that cache, we format it into a response message and publish it to the response topic that 
was built by NATS under the hood.

### Request message
```json
{
    "request_id" : "some-uuid", 
    "body": {
        "last_contact_filter": "2020-07-15T15:25:42.000Z" // Only get devices that were last contacted after this time
    }
}
```


### Response message
Non empty response
```json
{
    "request_id" : "some-uuid", 
    "body": [
        {
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-08-27T02:23:59",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK"
            }
        }
    ],
    "status": 200
}
```

Response when cache is still being built
```json
{
    "request_id": "some-uuid",
    "body": "Cache is still being built",
    "status": 202
}
```

Response when no devices satisfy specified filters
```json
{
    "request_id": "some-uuid",
    "body": "No devices were found for the specified filters",
    "status": 404
}
```

