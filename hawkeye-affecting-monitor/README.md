# Table of contents
  * [Description](#description)
  * [Affecting monitoring](#affecting-monitoring)
  * [Capabilities used](#capabilities-used) 
  * [Running in docker-compose](#running-in-docker-compose)

# Description
The objective of `hawkeye-affecting-monitor` is to detect Affecting issues in Ixia devices by analyzing metrics included
in the results of Ixia's tests executions, also known as tests results.

# Work Flow

## Preparations and considerations
Before tests results are analyzed, the process discards any device that is not cached in `hawkeye-customer-cache`.

When a device is processed, all the tests results of the last **15 minutes** are claimed to `hawkeye-bridge`. The process
will then analyze each test result sequentially, as the way every test result is analyzed depends on the outcome of the
analysis of the previous test result.

> The order in which tests results are processed depends on the date they were recorded by Ixia. Tests results are
> sorted by date in ascending order, i.e. the oldest ones are processed first.

The way a test result is processed depends on its status, which can be either `PASSED` or `FAILED`.

> There is an additional status called `ERROR`, but these kind of statuses are not analyzed as they arise as a consequence
> of a bad configuration of the test, or the probes involved in it.

## Test result with PASSED status

First thing checked when a PASSED test result is analyzed is the existence of a Service Affecting ticket for the
current device. If no ticket is found, the test result won't be analyzed because the device has been OK until now and it's
still OK.

If the ticket does exist, the next step is find the last note appended to the ticket whose test type matches with
the test type of the test result. If this note doesn't exist, then the process stops here for the same reason of the previous
paragraph: the device has been OK until now, and it's still OK.

In case that the last note appended to the ticket exists, and it was appended because of a previous FAILED test result, a new
note to report the current PASSED status is built and queued for append at the end of the process. If the last note refers
to a previous PASSED status, no note is appended for the same reason behind previous casuistics: the device has been OK until
now, and it's still OK.

## Test result with FAILED status

First thing checked when a FAILED test result is analyzed is the existence of a Service Affecting ticket for the
current device. If no ticket is found then a new Service Affecting ticket is created, and a new note to report the current FAILED
status is built and queued for append at the end of the process.

If the ticket does exist, and it's resolved, the process will first unresolve the detail associated to the device in
that ticket. After that, a new note to report the current FAILED status is built and queued for append at the end of the process.

If the ticket does exist, and it's open, the next step is find the last note appended to the ticket whose test type matches with
the test type of the test result. If this note doesn't exist, then a new note to report the current FAILED status is built and queued
for append at the end of the process.

In case that the last note appended to the ticket exists, and it was appended because of a previous PASSED test result, a new
note to report the current FAILED status is built and queued for append at the end of the process. If the last note refers to a previous
FAILED status, no note to report the current FAILED status will be built nor appended to the ticket.

## Final step: append all notes built during the process

After having analyzed all tests results of a device, the process will append to the corresponding ticket all the notes that
were built for that device during the process with a single request to Bruin. The notes will be posted in the same order
they were built throughout the process.

# Capabilities used
- [Hawkeye bridge](../hawkeye-bridge/README.md)
- [Hawkeye customer cache](../hawkeye-customer-cache/README.md)
- [Bruin bridge](../bruin-bridge/README.md)
- [Notifier](../notifier/README.md)

# Running in docker-compose
`docker-compose up --build redis hawkeye-bridge bruin-bridge notifier nats-server hawkeye-customer-cache hawkeye-affecting-monitor`
