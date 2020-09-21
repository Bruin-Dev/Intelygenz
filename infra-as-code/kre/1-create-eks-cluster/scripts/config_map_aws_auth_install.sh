#!/bin/bash

bucket_name=$1
kubeconfig_folder=$2

echo "Downloading config_map_aws_auth from bucket ${bucket_name}"
aws s3 cp s3://"${bucket_name}"/config_map_aws_auth /tmp/config_map_aws_auth
kubectl apply -f /tmp/config_map_aws_auth --kubeconfig "${kubeconfig_folder}"