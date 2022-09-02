<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

1. CONCEPTS
	1. [Monorepo](pipeline/BASIC_CI_CONFIGURATION.md)send
	2. [Semantic Release](pipeline/BASIC_CI_CONFIGURATION.md)
	3. [Infrastructure as code](pipeline/BASIC_CI_CONFIGURATION.md)
	4. [Datalake](pipeline/BASIC_CI_CONFIGURATION.md)
	5. [Kafka](pipeline/BASIC_CI_CONFIGURATION.md)
2. PIPELINES
	1. [BASIC CONFIGURATIONS](pipeline/BASIC_CI_CONFIGURATION.md)
		1. [Semantic release](pipeline/BASIC_CI_CONFIGURATION.md#11-semantic-release)
		2. [AIVEN](pipeline/BASIC_CI_CONFIGURATION.md#12-aiven)
		3. [AWS](pipeline/BASIC_CI_CONFIGURATION.md#13-aws)
		4. [Snowflake]()
		5. [PIPELINES RULES](pipeline/PIPELINE_RULES.md)
			1. [Add new section](pipeline/PIPELINE_RULES.md#add-new-section)
			2. [Add new template](pipeline/PIPELINE_RULES.md#add-new-template)
3. DOCUMENTATION
	1. [Organization](DOCUMENTATION.md#1-docs-organization)
		1. [Rules](DOCUMENTATION.md#2-rules)
		2. [Tools](DOCUMENTATION.md#3-tools)
	2. [MetTel Decisions](decisions/README.md)
	3. [Metrics definitions](metrics-definitions/README.md)
	4. [Diagrams](diagrams/README.md)
	5. [Logging](logging/README.md)
4. DEVELOPMENT RULES
	1. [Branch name convention]()
	2. [Semantic release]()
5. WORK IN A LOCAL ENVIRONMENT
	1. [Launch docker compose](kafka/LAUNCH_DOCKER_COMPOSE.md)
6. DATALAKE
	1. [Create private key for a user/service](snowflake/README.md#1-create-a-private-key-for-a-user)
		1. [Key rotation policy](snowflake/README.md#2-key-rotation-policy)
		2. [Add a new provider](snowflake/README.md#3-add-a-new-provider)
		3. [Rules](snowflake/README.md#4-rules)
7. MANUAL PROCEDURES
	1. [Vendor access to the API](procedures/API_VENDOR_ACCESS.md)
8. MANUAL CONFIGURATIONS
	1. [AWS SSO Okta identity provider](manual_configurations/OKTA_CONFIGURATIONS.md)
		1. [Revoke Session token](manual_configurations/OKTA_CONFIGURATIONS.md#revoke-permissions)
	2. [AWS SSO Okta JWT token](manual_configurations/OKTA_JWT.md)
9. AUDIT EVENTS
    1. Automation
       1. Communication between services
          1. [Messages Bus](logging/events/0-messages-bus.md)
       2. Use Cases
           1. [Service outage](logging/events/1-service-outage.md)
           2. [BYOB IPA Queue](logging/events/2-BYOB-IPA-queue.md)
           3. [HNOC forwarding](logging/events/3-HNOC-forwarding.md)
           4. [SA forwarding to ASR](logging/events/4-SA-forward-to-ASR.md)
           5. [TNBA Monitor](logging/events/5-TNBA-monitor.md)
           6. [Ticket severity](logging/events/6-ticket-severity.md)
           7. [Ticket creation outcomes](logging/events/7-ticket-creation-outcome.md)
           8. [Service affecting](logging/events/8-service-affecting.md)
           9. [InterMapper Outage Monitoring](logging/events/9-intermapper-monitor.md)
           10. [Ixia Outage Monitoring](logging/events/10-ixia-outage-monitoring.md)
       3. Bridges
          1. [Bruin Bridge](logging/events/11-bruin-bridge.md)
          2. [VeloCloud Bridge](logging/events/12-velocloud-bridge.md)
          3. [Notifications Bridge](logging/events/13-notifications-bridge.md)
          4. [Email Bridge](logging/events/14-email-bridge.md)
          5. [Forticloud Bridge](logging/events/15-forticloud-bridge.md)
    2. Infrastructure
        1. [Lambda Parameter-Replicator](lambda/PARAMETER_REPLICATOR.md)

