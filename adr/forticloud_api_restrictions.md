# Title Forticloud API restrictions

## Date

10/10/2022

## State

PROPOSED

## Context

The following limits apply to FortiLAN Cloud APIs:

- From the same source IP address, 6 auth requests are accepted per minute and across different source IP addresses, 60 auth calls are accepted per minute. 
- From the same source IP address, 60 other API calls are accepted per minute and across different source IP address, 600 other API calls are accepted per minute.

## Decision - Retry logic

A first approach was adding a retry both in the forticloud-cache and the forticloud-monitor. We end up using 
tenacity for this task after a spike and the values were tuned to our requirements in each service.

## Consequences

Retry was a featured needed eventually, so it was a good fast approach but sadly for this issue it feels more like a 
temporary path and even fails to solve the issue sometimes.

## Decision - New user

We thought that we could circumvent the issue by having a second user, thus increasing our api call limits.
And logic wise is a better idea to have two users as the services are doing different things and are independent.

## Consequences

A second user can be useful to avoid having to synchronize forticloud-cache and forticloud-monitor services
to avoid one service exhausting our api calls per minute while the other is trying to do the same.
But this idea was proven wrong later on as we found that the API limits are per instance,
so technically just by having several instances with the same user we can increase our api calls bandwidth.

Doubts raised about if this could cause the token requested by A being expired by B asking a new one. But the team
did a few tests and that didn't happen, in fact A and B token was valid between their time limits.

This helps a little but still fails to solve permanently the issue

## Alternatives

Team found that despite using different users the limit constraint is set at the IP level
so if we want to effectively use the instances and users with the retry logic we should study
how having several IPs. We currently has several IPs internally for each POD but the Kubernetes cluster
has only one exit to the Internet, limiting us to only 600 api calls it doesn't matter if
we use one or more users, the amount of api calls of all the instances would amount to the total for 
that IP.