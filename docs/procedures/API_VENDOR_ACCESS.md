## Pre requisites
- Okta Account
- AWS Account

## Description
This procedure explains how to give access to a specific vendor to the data highway API.

## Vendor requirements
- Provide a static trusted IP of the vendor

## MetTel configurations
MetTel needs to do these next steps:
- The Okta vendor account into OKTA group DATA-HIGHWAY-API
- Vendor profile filled with the organization name of their company.

## API gateway configurations
On the data highway team:
- Add the trusted static IP on the API gateway access policy.


