# Table of contents
  - [Service logic](#service-logic)
  - [Get customers](#get-customers)
      * [Description](#description)
      * [Request message](#request-message)
      * [Response message](#response-message)
# Service logic
This service will ask all velocloud-bridge for all the edges across all the velocloud instances.

Once it has all velocloud devices it will discard any device with no serial.

After that it will use the serial number to get the client ID from Bruin(bruin-bridge). 
It will ask for the management status of that device under that client ID.

If the management status is one of the following: 
"Pending", "Active – Gold Monitoring", "Active – Platinum Monitoring"
the device will be considered active and added to a temporal map.

When all edges for a host are processed it will store that map in redis(under one key), so it's not lost between executions.
This means we will store one partial cache for each velocloud host once it has finished, without waiting for the rest of the host to complete.

On start and each 4 hours, the process should be executed again to refresh the cache, but the substitution will only be 
done when process is finished and the length of the new cache is greater than 0 elements.

# Get Customers
### Description
When the customer cache receives a request from topic customer.cache.get it makes a callback to function get_customers.
If the request message is in the correct format then it should grab the caches from the storage_repository of the hosts in the `filter` key in the `body` key of the request message. And if there are anything in `enterprise_id` list then it will filter the cache even more to only include those enterprises. If the `filter` is an empty list (i.e. no filter), it will grab all the caches by default.
Another filter that can be requested to be applied through the rpc_request is the `last_contact`. This filter, if the value is not `None`, essentially would check the `last_contact` value of each edge in the cache and filter out any edges with a `last_contact` time before the `last_contact` time specified in the RPC's payload.

If the cache is empty then the `body` for the response message will send a message indicating that the cache is still
being built for the requested Velocloud hosts.

And with that cache, we format it into a response message and publish it to the response topic that 
was built by NATS under the hood.
### Request message
```
{
    "request_id" : uuid(), 
    "body": {"filter": {"mettel.velocloud.com":[]} # host: [list of enterprise_ids],
             "last_contact_filter": "2020-07-15T15:25:42.000Z"} #Only get edges that were last contacted after this time
            }
}
```
### Response message
Non empty cache response
```
{
    "request_id" : uuid(), 
    "body" :{
              customer_devices:[{
                                  'edge': edge_ids(velocloud),
                                  'last_contact': last_contact,
                                  'serial_number': serial_number,
                                  'bruin_client_info': bruin_client_info
                                 }
                               ]
             }, 
    "status": 200
}
```
Empty cache response
```
{
  'request_id': msg['request_id'],
   "body": "Cache is still being built for host(s): <insert_list_of_velos_here>",
   "status": 202
}
```