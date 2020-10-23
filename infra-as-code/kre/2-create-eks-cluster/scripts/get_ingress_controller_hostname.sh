#!/bin/bash

bucket_name=$1
kubeconfig_dir=$2

NS="-n kube-system"
LABELS="-l app=nginx-ingress,component=controller"
KUBECONFIG_DIR="--kubeconfig=${kubeconfig_dir}"

function download_kube_config() {
    if [ ! -f "${kubeconfig_dir}" ]; then
      aws s3 cp s3://"${bucket_name}"/kubeconfig "${kubeconfig_dir}"
    fi
}

function get_ingress_controller_hostname() {
    NGINX_INGRESS_POD=$(kubectl get pod ${LABELS} ${KUBECONFIG_DIR} ${NS} -o jsonpath="{.items[0].metadata.name}")
    if [ -z "$NGINX_INGRESS_POD" ]
    then
      echo -n "ingress_not_deployed"
      exit 0
    fi
    while [[ $(kubectl get pods ${NGINX_INGRESS_POD} ${KUBECONFIG_DIR} ${NS} \
            -o 'jsonpath={..status.conditions[?(@.type=="ContainersReady")].status}') != "True" ]];
    do
        sleep 5;
    done
    ingress_controller_hostname=$(kubectl get svc ${KUBECONFIG_DIR} ${LABELS} ${NS} -o jsonpath="{.items[0].status.loadBalancer.ingress[0].hostname}")
    echo -n "${ingress_controller_hostname}"
}

function main() {
    download_kube_config
    get_ingress_controller_hostname
}

main