<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

1. CONCEPTS
	1. [Monorepo](pipeline/BASIC_CI_CONFIGURATION.md)
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
	1. [Vendor access to the API](manual_procedures/API_VENDOR_ACCESS.md)
	2. [Switch Automation Engine region](manual_procedures/SWITCH_AUTOMATION_ENGINE_REGION.md)
8. MANUAL CONFIGURATIONS
	1. [Init Automation Engine project](manual_configurations/INIT_AUTOMATION_PROJECT.md)
	2. [AWS SSO Okta identity provider](manual_configurations/OKTA_CONFIGURATIONS.md)
		1. [Revoke Session token](manual_configurations/OKTA_CONFIGURATIONS.md#revoke-permissions)
	3. [AWS SSO Okta JWT token](manual_configurations/OKTA_JWT.md)
9. AUDIT EVENTS
     1. Automation
          * Bridges
             * [Bruin Bridge](logging/events/bruin-bridge.md)
             * [DiGi Bridge](logging/events/digi-bridge.md)
             * [DRI (Data Remote) Bridge](logging/events/dri-bridge.md)
             * [Email Bridge](logging/events/email-bridge.md)
             * [Hawkeye / Ixia Bridge](logging/events/hawkeye-bridge.md)
             * [Notifications Bridge](logging/events/notifications-bridge.md)
             * [ServiceNow Bridge](logging/events/servicenow-bridge.md)
             * [VeloCloud Bridge](logging/events/velocloud-bridge.md)

          * Communication between services
             * [Messages Bus](logging/events/messages-bus.md)

          * Use cases
              * DiGi
                  * [Reboot Report](logging/events/digi-reboot-report.md)

              * Fraud
                  * [Alerts Monitor](logging/events/fraud-monitor.md)

              * Hawkeye / Ixia
                  * [Outage Monitor](logging/events/hawkeye-outage-monitor.md)

              * InterMapper
                  * [Outage Monitor](logging/events/intermapper-outage-monitor.md)

              * LuminAI
                  * [Billing Report](logging/events/lumin-billing-report.md)

              * Tasks scheduling
                  * [Task Dispatcher](logging/events/task-dispatcher.md)

              * VeloCloud
                  * Reporting
                      * [Last Contact Report](logging/events/last-contact-report.md)
                  * SD-WAN Monitoring
                      * [Affecting Monitor](logging/events/service-affecting-monitor.md)
                      * [Gateway Monitor](logging/events/gateway-monitor.md)
                      * [Outage Monitor](logging/events/service-outage-monitor.md)
                      * [TNBA Monitor](logging/events/tnba-monitor.md)

          * Use cases with bridge capabilities
             * VeloCloud
                 * [Customer Cache](logging/events/customer-cache.md)

             * Hawkeye / Ixia
                 * [Customer Cache](logging/events/hawkeye-customer-cache.md)

     2. Infrastructure
         * [Lambda Parameter-Replicator](lambda/PARAMETER_REPLICATOR.md)

