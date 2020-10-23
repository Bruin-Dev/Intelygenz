#!/bin/bash

bucket_name=$1
kubeconfig_folder=$2

echo "Downloading kubeconfig from bucket ${bucket_name}"
aws s3 cp s3://"${bucket_name}"/kubeconfig /tmp/kubeconfig
helm repo add stable https://kubernetes-charts.storage.googleapis.com/
helm repo update
helm upgrade --install \
     --namespace kube-system \
     --version 1.40.2 \
     nginx-ingress \
     stable/nginx-ingress \
     --kubeconfig "${kubeconfig_folder}"