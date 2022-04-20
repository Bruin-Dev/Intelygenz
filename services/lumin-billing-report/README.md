# Lumin billing report
* [Description](#description)
* [Components](#components)
* [Examples](#examples)
* [Capabilities used](#capabilities-used)
* [Running in docker-compose](#running-in-docker-compose)

# Description
This service automates requesting billing information for a given customer from the Lumin.AI service provider,
generating a summary HTML email and attaching a csv with all data for the current billing period.

# Components
- ***clients/EmailClient***
    Interface for SMTP client.
- ***clients/LuminBillingClient***
    Interface for Lumin.AI Billing REST API. See [documentation](readme-resources/lumin-ai-billing-api.pdf).
- ***repositories/LuminBillingRepository***
    Main entrypoint for service access to Lumin.AI Billing API. Has one method that returns _all_ results for a given 
    date range and billing event type.
- ***repositories/TemplateRenderer***
    Template renderer for lumin billing report template and accompanying csv file.
- ***actions/BillingReport***
    Main report building logic, triggered on first day of month as APScheduler asyncio cron.

# Examples
![example](readme-resources/examples/lumin-example.png)
And a sample csv [attachment](readme-resources/examples/lumin-example.csv)

# Capabilities used
This service is self-contained, i.e., it does not require access to NATS or Redis, or any other microservice within the Automation Engine.

![IMAGE: lumin-billing-report_microservice_relationships](/docs/img/system_overview/isolated_services/lumin-billing-report_microservice_relationships.png)

# Running in docker-compose
__TODO__
