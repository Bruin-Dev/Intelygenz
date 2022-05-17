# {{capability_name}}
* [Description](#description)
* [Links](#links) {{optional}}
* [Requests](#requests)
    * [{{request_name}}](#{{request_name}})
* [Local testing](#local-testing)

# Description
{{short capability description using
[ubiquitous terms](https://docs.google.com/document/d/1QH0ESuO7rEEAjzj3I3_pnbl1E2ClOM6iW-bxYSsfHqw) when possible:
what is the proxied service being used for?}}

![IMAGE: {{service_diagram_name}}](doc/{{service_diagram_path}}) {{optional}}

# Links
{{optional list of useful links, proxied service API, documentation, swagger, etc.}}

# Requests
## {{request_name}}
{{short request description using
[ubiquitous terms](https://docs.google.com/document/d/1QH0ESuO7rEEAjzj3I3_pnbl1E2ClOM6iW-bxYSsfHqw) when possible:
what is the proxied endpoint behaviour? what is this request being used for?}}

- Topic name: `{{request_topic_name}}`
- Proxied endpoint: `{{proxied_endpoint_path}}`
- ([Endpoint documentation]({{proxied_endpoint_documentation_link}})|No endpoint documentation available)
- Endpoint message json schemas: {{if no endpoint documentation available or not useful enough}}
    - [Endpoint request]({{src/api/endpoint_request.json}})
    - [Endpoint response 1]({{src/api/endpoint_response_1.json}})
    - [Endpoint response 2]({{src/api/endpoint_response_2.json}})
- Custom message json schemas:
    - [Custom request]({{src/api/custom_request.json}})
    - [Custom response 1]({{src/api/custom_response_1.json}})
    - [Custom response 2]({{src/api/custom_response_2.json}})

# Local testing
{{steps to get the service up and running in a local environment}}  
{{`docker-compose up --build`}}

## Snippets
{{code snippets to test the service}}