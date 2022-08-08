# Table of contents
* [Integration tests server](#integration-tests-server)
  * [What is this server for?](#what-is-this-server-for?)
  * [How does it work?](#how-does-it-work?)
  * [What is a scenario?](#what-is-a-scenario?)
  * [What is a route?](#what-is-a-route?)
    * [What is a path?](#what-is-a-path?)
    * [What is a handler?](#what-is-a-handler?)
  * [How are scenarios built?](#how-are-scenarios-built?)
* [Scenario implementation](#scenario-implementation)
  * [Given](#given)
  * [When](#when)
  * [Then](#then)
    * [Awaits](#awaits)
* [Run the server](#run-the-server)
  * [Local environment](#local-environment)
  * [Ephemereal environment](#ephemereal-environment)

# Integration tests server
## What is this server for?
This server considers the automation-engine system as a black box. 
It aims to test every integration in-between the system by asserting outgoing HTTP or GRPC traffic.


## How does it work?
The server will run a list of scenarios when issuing a PUT request to the `_run_scenarios` REST endpoint.
Scenarios can mock, spy or wait any HTTP or GRPC request to check any integration points for a specific execution flow.
These scenarios should validate a correct data transmission rather than to validate the data being transmitted;
(the data validation should be done with unit tests or specific service integration tests).

## What is a scenario?
A scenario is a collection of `given` statements that are modeled as a collection of [routes](/src/application/route.py).
The server behaviour will vary depending on the active scenario as it is actually the scenario the one that handles the GRPC or HTTP requests.
The scenario will delegate the request handling either to a matching route or to a default behaviour.

## What is a route?
A route expresses the relationship between a path and a [handler](/src/application/handler.py) and can be seen as a `given` statement.
Scenarios will usually look for any route matching a given path and will delegate the request to the corresponding handler.

### What is a path?
A path is a stadard URI path that can be parametrized following [starlette http routing](https://www.starlette.io/routing/#http-routing) 
(parameters won't be saved).

### What is a handler?
A handler is just an `unittest.mock.AsyncMock` wrap.
Keep in mind that every request that will go through the server will delegate its execution to a handler.
This means we have the power of making `AsyncMock` asserts on any route by doint `route.handler.assert_awaited_...()`

# How are scenarios built?
First, note that there is no DSL to declare the scenarios; they are built using code.
You can duplicate the [example scenario](/src/application/scenarios/example_scenario.py) and add it to the list of scenarios to be executed 
at the [http server](/src/application/servers/http/http.py)

Any scenario should inherit from the [base scenario](/src/application/scenario.py);
this will give you access to some useful shorthand methods to help design the scenarios and will populate the scenario with some default routes.

# Scenario implementation
## Given
You can mock requests by return static data. E.g.:
```python
self.given("/any/path", WillReturn("any_payload"))
```

You can also mock requests and return dynamica data or implement any kind of state.
The arguments passed to the anonymous functions will be the ones that are being passed from the http and grpc servers.
```python
state: Dict[str, str] = {}
def dynamic_response(request: Request):
  mutate_state(state, request)
  return build_response(request)
  
self.given("/any/path", WillExecute(dynamic_response))
# etc...
```

## When
To start any execution within automation-engine system, specific clients must be crafted to either 
send a request to an endpoint, store some information in a Redis storage, etc.
All those clients should be located in the [clients module](/src/application/clients)


## Then
Route handlers are `AsyncMocks`; you can use `AsyncMock` methods to make asserts if needed:
```python
route = self.given("/any/path", WillReturn("any_payload"))
route.handler.assert_awaited_once()
route.handler.assert_awaited_once_with({})
# etc...
```

*Remember these tests aim to validate the data transmission, not the data itself!*

### Awaits
You can stop a scenario execution and wait for any endpoint to be called:
```python
await self.route("/any/path").was_reached(25.0)

# or
route = self.given("/any/path", WillReturn("any_payload"))
await route.was_reached(25.0)
```

This should work as a scenario assert.

# Run the server
## Local environment
1. `docker-compose -f docker-compose.yml -f docker-compose.integration-tests.yml up -d`.  
   You can start any services you want, but it should be better to start them all to try to mimic a real environment.  
2. `curl -X PUT "http://localhost:8001/_run_scenarios"`  
   _Trick: you can pipe a JSON processor to the curl output to get a formatted result._  
   _e.g using [jq](https://stedolan.github.io/jq/) `curl -X PUT "http://localhost:8001/_run_scenarios" | jq`_
3. (Optional) You can check the scenarios execution by doing `docker-compose logs -f integration-tests`
4. (Optional) Once the tests are finished, you can run `docker-compose kill`
## Ephemereal environment
Currently this server is not ready to be run in an ephemereal environment.
The help of a devops is needed.
