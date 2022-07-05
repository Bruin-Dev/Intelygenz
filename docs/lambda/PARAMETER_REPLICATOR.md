<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# 1. Summary

Parameter Store is a capability of AWS Systems Manager that provides secure, hierarchical storage for configuration data management and secrets management. This service is only available in the region where is deployed. We use it to set configuration of Automation-Engine app. But if a desaster occurs in the main region we need to have the parameters replicated en the stand-by region to redeploy the app.

Parameter-replicator is a phython lambda that replicate parameters from one region to another. If any parameter change, that change will be replicated in the other region, by this way we have a configuration ready to run the application in the mirror region. This lambda also run ones a day to create a parameter backup and store in S3.

# 1. Diagram

[parameter-replicator.drawio.svg](../diagrams/parameter-replicator.drawio.svg)