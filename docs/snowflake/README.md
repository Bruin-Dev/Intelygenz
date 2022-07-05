<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# 1. Create a private key for a user/service
To create a new user follow the [link](https://docs.snowflake.com/en/user-guide/key-pair-auth.html#configuring-key-pair-authentication) from snowflake about key creation

It's only allowed to create users with keys to automate connection between services. If we need a key for testing purposes
should be a temporary user or in a development infrastructure. Important to know that only a SECURITYADMIN user can modify users
to have a key pair access.

# 2. Key rotation policy
Key rotation is a must to have a high security standard, at this moment is important to know is a manual process, each first
week of the month should be a calendar task in the devops team to change it a redeployment the infrastructure with these new keys.

Right now is not automated because no make sense to do it, you have to have a static user that can modify these stuff
manually in the web, if we discover a way to do it automatically without a static user or a bastion one we could think about it.

# 3. Add a New provider

# 4. Rules
+ Each private key must have a passphrase.
+ Each new provider must have their own key
+ Devops team must renew keys each month and redeploy the infra.

---
With passion from the [Intelygenz](https://www.intelygenz.com) Team @ 2021
