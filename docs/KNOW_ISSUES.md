
# Known Issues

## Data Highway

### API gateway route throttling
#### Description
The api gateway made with AWS have an issue related to the route route throttling. This happends because the configuration made with
open api and AWS is not clear where to put the throttling configuration. Each time a new deployment is made, the throttling configuration
resets to the default values.

The name of the environments are:
- data-highway-HTTP-API-develop
- data-highway-HTTP-API-master
#### How to fix it
The temporary fix is based on a manual interaction. Access to the API gateway configuration of AWS, select the environment data-highway-HTTP-API-develop or data-highway-HTTP-API-master and click under protection the button throttling. Inside the configuration of the throttling, update the Default route throttling. Use the values 100 on the Rate limit and burst limit.
#### Extra information
The file of the centralized open api is located in the path microservices/api/openapi_3.yaml of the datalake(Data highway) project.
The deployment file of the API is located infrastructure/deployments/aws_api_gateway_openapi.tf.