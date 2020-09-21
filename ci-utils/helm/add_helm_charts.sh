#!/bin/bash

HELM_CHARTS_TO_ADD=$1

oIFS="$IFS"
IFS=';' read -ra ADDR <<< "$HELM_CHARTS_TO_ADD"
for i in "${ADDR[@]}"; do
    repository_name=$(echo ${i} | cut -d " " -f 1)
    repository_url=$(echo ${i} | cut -d " " -f 2)
    echo "repository_name is ${repository_name}"
    echo "repository_url is ${repository_url}"
    helm repo add "${repository_name}" "${repository_url}"
done
IFS="$oIFS"
unset oIFSs