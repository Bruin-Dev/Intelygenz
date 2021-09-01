locals {
  config_map_aws_auth = <<CONFIGMAPAWSAUTH
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: ${aws_iam_role.iam_role_node.arn}
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
  mapUsers: |
   - userarn: arn:aws:iam::374050862540:user/angel.costales
     username: angel.costales
     groups:
       - system:masters
CONFIGMAPAWSAUTH

  envs_file = <<ENVSFILE
#!/bin/sh
export AWS_EFS_ID="${aws_efs_file_system.efs_file_system.id}"
export AWS_DEFAULT_REGION="${local.aws_default_region}"
ENVSFILE
}
