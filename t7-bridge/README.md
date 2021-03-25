# Table of contents
  * [T7 API](#bruin-api)
    * [Description](#description)
  * [Get Prediction](#get-prediction)
    * [Description](#description-1)
    * [Request message](#request-message)
    * [Response message](#response-message)
- [Running in docker-compose](#running-in-docker-compose)


# Konstellation
## Description

T7 Bridge is used to make calls to Konstellation.

For now, it allows to get a prediction about the next best action that can be taken
to move forward on the resolution of a ticket.

## GRPC generated code

In the code necessary to implement the gRPC calls, we import two files generated
([public_input_pb2.py](src/application/clients/generated_grpc/public_input_pb2.py),
[public_input_pb2_grpc.py](src/application/clients/generated_grpc/public_input_pb2_grpc.py)) from the definition of the
[protocol buffer](https://gitlab.intelygenz.com/t7-team/met002-t7p-us/kre-runtime/-/blob/master/tnba/public_input.proto)
of the [project kre-runtime](https://gitlab.intelygenz.com/t7-team/met002-t7p-us/kre-runtime) compiling the protocol
buffer like:

```shell script
python -m grpc_tools.protoc -I../../protos --python_out=. --grpc_python_out=. ../../protos/route_guide.proto
```




# Get Prediction
## Description
To claim a prediction for a specific Bruin ticket, a RPC call to topic `t7.prediction.request` must be made.
The request message must a `body` key with the following fields:
- `ticket_id`. Integer field representing the ID of a ticket of Bruin system.

As usual, the response message will have the following fields:
- `body`. The body of the response. Can be either an object or a string.
- `status`. The statys code of the response. Indicates whether the request went fine or not.

## Scenarios
### No `body` specified in request
#### Request
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC"
}
```

#### Response
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": "You must specify {..\"body\": {\"ticket_id\"}..} in the request",
    "status": 400,
}
```

### Missing parameters in the `body` of the request
#### Request
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": {
        "ticket_id": 123
    }
}
```

#### Response
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": "You must specify {..\"body\": {\"ticket_id\"}..} in the request",
    "status": 400,
}
```

### Konstellation returning a response with errors
#### Request
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": {
        "ticket_id": 123
    }
}
```

#### Response
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": [
        {
            "assetId": "VC1234567",
            "error": {
                "code": "error_in_prediction",
                "message": "Error executing prediction: The labels ['Line Test Results Provided'] are not in the \"Task Result\" labels map."
            },
        },
        {
            "assetId": "VC1122334",
            "predictions": [
                {
                    "name": "Repair Completed",
                    "probability": 0.9484384655952454
                },
                {
                    "name": "Holmdel NOC Investigate",
                    "probability": 0.1234567890123456
                },
            ],
        }
    ],
    "status": 200
}
```

### Konstellation returning a response without errors
#### Request
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": {
        "ticket_id": 123
    }
}
```

#### Response
```json
{
    "request_id": "kNxC7FxXpg5ApdgGaX7otC",
    "body": [
        {
            "assetId": "VC1234567",
            "predictions": [
                {
                    "name": "Request Completed",
                    "probability": 0.1823748273483734
                },
                {
                    "name": "Wireless Repair Intervention Needed",
                    "probability": 0.8287249348922389
                },
            ],
        },
        {
            "assetId": "VC1122334",
            "predictions": [
                {
                    "name": "Repair Completed",
                    "probability": 0.9484384655952454
                },
                {
                    "name": "Holmdel NOC Investigate",
                    "probability": 0.1234567890123456
                },
            ],
        }
    ],
    "status": 200
}
```

# Running in docker-compose
`docker-compose up --build redis nats-server t7-bridge`