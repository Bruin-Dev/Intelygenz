

# AC-2 Account Management
## 1. Automated System Account Management
#### 1.1 Description
Support the management of system accounts using [GSA S/SO or Contractor recommended automated mechanisms as approved by the GSA CISO and AO]
#### 1.2 Implementation
Accounts are managed by Okta software connected to AWS IAM identity provider, the configurations used are following [this guide](../manual_configurations/OKTA_CONFIGURATIONS.md)

## 2. Automated Temporary and Emergency Account Management
#### 2.1 Description
Automatically [disables] temporary and emergency accounts after [no more than 90 days].
#### 2.2 Implementation
Accounts are managed by Okta software.
#### 2.3 Procedure
MetTel is in charge of creation, deactivation or deleting users in their organization. Temporary accounts and emergency accounts must be managed manually by MetTel and the deactivation of these kind of accounts.
#### 2.4 Testing
After deactivating a user following this [Link to Okta](https://help.okta.com/en-us/Content/Topics/users-groups-profiles/usgp-deactivate-user-account.htm) go to
the AWS account and check under this [link to IAM Identity center](https://us-east-1.console.aws.amazon.com/singlesignon/identity/home) and check the deactivated user.

## 3. Disable Accounts
#### 3.1 Description
Disable accounts within [30 days] when the accounts:
(a)        Have expired;
(b)        Are no longer associated with a user or individual;
(c)        Are in violation of organizational policy; or
(d)        Have been inactive for [30 days].
#### 3.2 Implementation
Accounts are managed by Okta software. An account that was disabled from Okta will be disabled on AWS when Expired, no longer associated with a user or individual, violation of a organization policy or have been inactive for 30 days.
#### 3.3 Procedure
MetTel is in charge of creation, deactivation or deleting users in their organization. Each of these actions are automatically replicated to the connected AWS account with the Oauth Okta system and AWS. 
#### 3.4 Testing
After deactivating a user following this [Link to Okta](https://help.okta.com/en-us/Content/Topics/users-groups-profiles/usgp-deactivate-user-account.htm) go to
the AWS account and check under this [link to IAM Identity center](https://us-east-1.console.aws.amazon.com/singlesignon/identity/home) and check the deactivated user.
#### 3.5 Extra information and links
- [Deactivate and delete users accounts](https://help.okta.com/en-us/Content/Topics/users-groups-profiles/usgp-deactivate-user-account.htm)
- [OKTA AWS IDP](https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html)

## 4. Automated Audit Actions
#### 4.1 Description
Automatically audit account creation, modification, enabling, disabling, and removal actions.
#### 4.2 Implementation
The implemation of the audit of the account is automatically enabled by AWS.
#### 4.3 Testing
Following the next [link to cloudtrail](https://us-east-1.console.aws.amazon.com/cloudtrail/home) is posible to query the user events and actions. 
#### 4.4 Extra information and links
- [AWS Security logging and monitoring](https://docs.aws.amazon.com/singlesignon/latest/userguide/security-logging-and-monitoring.html)
- [AWS logging cloudtrail](https://docs.aws.amazon.com/singlesignon/latest/userguide/logging-using-cloudtrail.html)
- [AWS Cloudwatch integration](https://docs.aws.amazon.com/singlesignon/latest/userguide/cloudwatch-integration.html)

## 5. Inactivity Logout
#### 5.1 Description
Require that users log out when [they have completed their workday].
#### 5.2 Implementation
This points must be done by loging out by the user from the laptops computers provided by MetTel.

# AC-3 Access Enforcement
## 1. Access Enforcement
#### 1.1 Description
Enforce approved authorizations for logical access to information and system resources in accordance with applicable access control policies.
#### 1.2 Implementation
This part was implemented eliminating all the permisions from terraform and IAM groups, giving only the needed ones for normal procedures and actions on AWS.
#### 1.3 Extra information and links
- [API Permissions](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/ec2-api-permissions.html)

# AC-4 Access Enforcement
#### 1.1 Description
Enforce approved authorizations for controlling the flow of information within the system and between connected systems based on [Web Service Security (WS Security), WS-Security Policy, WS Trust, WS Policy Framework, Security Assertion Markup Language (SAML), extensible Access Control Markup Language (XACML)].
#### 1.2 Implementation

# AC-6 Least Privilege
#### 1. Least Privilege
#### 1.1 Description
Enforce approved authorizations for controlling the flow of information within the system and between connected systems based on [Web Service Security (WS Security), WS-Security Policy, WS Trust, WS Policy Framework, Security Assertion Markup Language (SAML), extensible Access Control Markup Language (XACML)].

#### 2. AC-6(1) Authorize Access to Security Functions
#### 2.1 Description
Authorize access for [any individual or role] to: 
(a)        [GSA S/SO or Contractor recommended security functions (deployed in hardware, software, and firmware) approved by the GSA CISO and AO]; and 
(b)        [Security-relevant information as approved by the GSA CISO and AO].
#### 2.2 Implementation
Priviliged accounts/roles on the system are restricted to the recomended employees and contrators to access recomended security functions and security relevant information.

#### 3. AC-6(2) Non-privileged Access for Nonsecurity Functions
#### 3.1 Description
Require that users of system accounts (or roles) with access to [all security functions (examples of security functions include but are not limited to: establishing system accounts, configuring access authorizations (i.e., permissions, privileges), setting events to be audited, and setting intrusion detection parameters, system programming, system and security administration, other privileged functions)] use non-privileged accounts or roles, when accessing nonsecurity functions.
#### 3.2 Implementation
This is manually configured with specific groups on IAM Indentity center with no privileged credentials, these groups are asociated to users(from Okta), these are not allowed to execute or see privileged resources/functions.

#### 4. AC-6(5) Privileged Accounts
#### 4.1 Description
Restrict privileged accounts on the system to [GSA S/SO or Contractor recommended employees and contractors as approved by the GSA CISO and AO].
#### 4.2 Implementation
Priviliged accounts on the system are restricted to the recomended employees and contrators.

#### 5. AC-6(9) Log Use of Privileged Functions
#### 5.1 Description
Log the execution of privileged functions.
#### 5.2 Implementation
All functions used are throwing logs on [cloudwatch](https://us-east-1.console.aws.amazon.com/cloudwatch/home). The functions that the project is using are AWS Lambda. All these logs starts with /aws/lamda/* prefix under cloudwatch.

#### 5. AC-6(10) Prohibit Non-privileged Users from Executing Privileged Functions
#### 5.1 Description
Prevent non-privileged users from executing privileged functions.
#### 5.2 Implementation
This is manually configured with specific groups on IAM Indentity center with no privileged credentials, these groups are asociated to users(from Okta), these are not allowed to execute or see privileged resources/functions.
