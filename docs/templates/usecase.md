# {{usecase_name}}
* [Description](#description)
* [Dependencies](#dependencies) {{optional if no dependencies are being used}}
* [Usecases](#usecases)
    * [{{usecase_name}}](#{{usecase_name}})
* [Local testing](#local-testing)

# Description
{{short usecase description using
[ubiquitous terms](https://docs.google.com/document/d/1QH0ESuO7rEEAjzj3I3_pnbl1E2ClOM6iW-bxYSsfHqw) when possible:
what is the proxied service being used for?}}

# Dependencies
{{list of dependencies being used with links to their README. E.g.
- [Customer cache](../customer-cache/README.md)
- [Notifier](../notifier/README.md)
- [Bruin bridge](../bruin-bridge/README.md)}}

![IMAGE: usecase_diagram_name](doc/{{service_diagram_path}}) {{optional}}

# Usecases
## {{usecase_name}}
> Scheduled execution (each {{scheduled_interval}}) {{optional}}

{{short service description using
[ubiquitous terms](https://docs.google.com/document/d/1QH0ESuO7rEEAjzj3I3_pnbl1E2ClOM6iW-bxYSsfHqw) when possible:
what is the proxied service being used for?}}

{{Detailed usecase implementation if needed}}

# Local testing
{{steps to get the service up and running in a local environment}}  
{{`docker-compose up --build`}}

## Snippets
{{code snippets to test the service}}
