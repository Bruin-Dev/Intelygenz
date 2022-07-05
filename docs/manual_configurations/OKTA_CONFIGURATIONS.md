## Pre requisites
- Okta Account
- AWS Account

## Description
Because of [FEDRAMP](https://www.fedramp.gov/) we need to implement as a team a IdP that control all users and permissions 
related to MetTel projects that are made by Intelygenz. For automatic synchronization we are going to create SCIM sync between
OKTA and AWS SSO, because of that, groups and users are going to be synced if someone deletes/create a group/user in Okta.

## Considerations
- Remove a user/group don't revoke the session tokens in AWS, the minimum duration of these tokens are of 1h. [Info here](https://docs.aws.amazon.com/singlesignon/latest/userguide/authconcept.html#sessionsconcept)
- Using the same Okta group for both assignments and group push is not currently supported. To maintain consistent group memberships between Okta and AWS SSO, you need to create a separate group and configure it to push groups to AWS SSO. [Info here](https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html)
- If you update a user’s address you must have streetAddress, city, state, zipCode and the countryCode value specified. If any of these values are not specified for the Okta user at the time of synchronization, the user or changes to the user will not be provisioned. [Info here](https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html)
- Entitlements and role attributes are not supported and cannot be synced to AWS SSO. [Info here](https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html)

## Steps
- Configure IdP with Okta, [this is the guide](https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html).
- Create the following groups:
  - OKTA-IPA-FED-INT-PRIVILEGED: Internal users Federated privileged group on the federal account. Administration accounts.
  - OKTA-IPA-FED-INT-NON-PRIVILEGED: Internal users Federated non privileged group on the federal account.
  - OKTA-IPA-COM-INT-PRIVILEGED: Internal users Commercial privileged group on the commercial account. Administration accounts.
  - OKTA-IPA-COM-INT-NON-PRIVILEGED: Internal users Federated privileged group on the commercial account. Administration accounts.
  - OKTA-IPA-FED-EXT-PRIVILEGED: External users Federated privileged group on the federal account. Administration accounts.
  - OKTA-IPA-FED-EXT-NON-PRIVILEGED: External users Federated non privileged group on the federal account.
  - OKTA-IPA-COM-EXT-PRIVILEGED: External users Commercial privileged group on the commercial account. Administration accounts.
  - OKTA-IPA-COM-EXT-NON-PRIVILEGED: External users Federated privileged group on the commercial account. Administration accounts.
- Associate permissions to groups. [Guide](https://docs.aws.amazon.com/singlesignon/latest/userguide/iam-auth-access-overview.html)
  - Privileged accounts will have general administrator permissions
  - Non privileged accounts will only have access to logs on cloud watch and grafana


## Revoke permissions
Because of the problem of token duration of 1h that can not be revoked from okta, there is a manual procedure to delete 
the access from AWS SSO. For revoking access follow [this guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_revoke-sessions.html)

---
With passion from the [Intelygenz](https://www.intelygenz.com) Team @ 2022
