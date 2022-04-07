# DRI bridge
* [Description](#description)
* [Links](#links)
* [Requests](#requests)
  * [Get DRI Parameter](#get-dri-parameter)
* [Running in docker-compose](#running-in-docker-compose)


# Description
DRI Bridge is used to make calls to the DRI API. The main call includes [get_dri_parameter](#get-dri-parameter) which is comprised of
three different endpoint calls to the DRI API.

![IMAGE: dri-bridge_microservice_relationships](/docs/img/system_overview/capabilities/dri-bridge_microservice_relationships.png)

# Links
Bruin API endpoints:
- https://api.dataremote.com/auth/login
- https://api.dataremote.com/acs/device/{serial_number}/parameter_returnid?data={ParameterSet}
- https://api.dataremote.com/acs/device/{serial_number}/parameter_tid?transactionid={TransactionID}
- https://api.dataremote.com/acs/device/{serial_number}/taskpending

# Requests
## Get DRI Parameter
The `get_dri_parameter` action is supposed to create a task_id from DRI and return the dri parameters of that completed task_id. 

First the DRI bridge must gets a rpc request sent to topic `dri.parameters.request` with a `serial_number` and `parameter_set`. Then
we first check if a task_id already exists for that serial. We check the redis first, and if it's not their we make a 
call to DRI to get the list of pending task ids. If no task id is found in either redis or the pending task id
list then we create a new task_id by making a call to DRI.

Once we receive the task id we then make another call to DRI to check if that task id has completed or not. We then send
the results back to the event bus.

```python
request_message = {
    'request_id': 123,
    'body': {
        'serial_number': 700059,
        'parameter_set': {
            'ParameterNames': [
                'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert',
                'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers',
                'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid',
                'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum',
                'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei',
                'InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress',
            ],
            'Source': 0,
        },
    },
}

complete_response_message = {
    'request_id': request_message['request_id'],
    'body': {
        'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.ModemImei': '864839040023968',
        'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Providers': 'ATT',
        'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimIccid': '89014103272191198072',
        'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.SimInsert': 'SIM1 Active',
        'InternetGatewayDevice.DeviceInfo.X_8C192D_lte_info.Subscribernum': '15245139487',
        'InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.MACAddress': '8C:19:2D:23:30:69',
    }, 
    'status': 200,
}

pending_response_message = {
    'request_id': request_message['request_id'],
    'body': 'Data is still being fetched from DRI for serial {serial_number}', 
    'status': 204,
}

rejected_response_message = {
    'request_id': request_message['request_id'],
    'body': 'DRI task was rejected for serial {serial_number}', 
    'status': 403,
}
```

# Running in docker-compose
`docker-compose up --build redis nats-server prometheus dri-bridge`
