#!/bin/bash

KRE_RECORD_ALIAS_NAME=$1
HOSTED_ZONE_NAME=$2
ACTION=$3
NS="-n kube-system"
NGINX_LABELS="-l app=nginx-ingress,component=controller"

function wait_until_check_ingress_is_ready() {
    NGINX_INGRESS_POD=$(kubectl get pod ${NGINX_LABELS} ${NS} -o jsonpath="{.items[0].metadata.name}")
    echo "NGINX_INGRESS_POD is ${NGINX_INGRESS_POD}"
    while [[ $(kubectl get pods ${NGINX_INGRESS_POD} ${NS} \
            -o 'jsonpath={..status.conditions[?(@.type=="ContainersReady")].status}') != "True" ]];
    do
        echo "Waiting for pod ${NGINX_INGRESS_POD} to be with ContainersReady status"
        sleep 5;
    done
    echo "Pod of nginx ingress ${NGINX_INGRESS_POD} is Running and with ContainersReady"
}

function get_action_verb() {
  if [[ "$ACTION" == "-u" ]]; then
    echo "UPSERT"
  elif [[ "$ACTION" == "-d" ]]; then
    echo "DELETE"
  fi
}

function do_action_in_route53_record() {
    echo "HOSTED_ZONE_NAME is ${HOSTED_ZONE_NAME}"
    echo "It's going to do action ${ACTION}"
    elb_dns_name=$(kubectl get svc ${NGINX_LABELS} ${NS} -o jsonpath="{.items[0].status.loadBalancer.ingress[0].hostname}")
    elb_hosted_zone_id=$(aws elb describe-load-balancers | jq -r --arg elb_dns_name $elb_dns_name '.LoadBalancerDescriptions | .[] | select(.DNSName==$elb_dns_name) | .CanonicalHostedZoneNameID')
    hosted_zone_id=$(aws route53 list-hosted-zones  | jq --arg HOSTED_ZONE_NAME $HOSTED_ZONE_NAME -r '.HostedZones | .[] | select(.Name==$HOSTED_ZONE_NAME) | .Id')
    echo "hosted_zone_id is ${hosted_zone_id}"
    identifier="${elb_hosted_zone_id}kre"
    ACTION_VERB=$(get_action_verb)
    JSON_STRING=$( jq -n \
                  --arg kre_record_alias_name "$KRE_RECORD_ALIAS_NAME" \
                  --arg elb_hosted_zone_id "$elb_hosted_zone_id" \
                  --arg elb_dns_name "$elb_dns_name" \
                  --arg identifier "$identifier" \
                  --arg ACTION_VERB "$ACTION_VERB" \
                  '{
                    "Comment": "Update kre record set",
                    "Changes": [
                      {
                        "Action": $ACTION_VERB,
                        "ResourceRecordSet": {
                          "Name": $kre_record_alias_name,
                          "Type": "A",
                          "AliasTarget": {
                            "HostedZoneId": $elb_hosted_zone_id,
                            "DNSName": $elb_dns_name,
                            "EvaluateTargetHealth": true
                          }
                        }
                      }
                    ]
                  }' )
    echo "$JSON_STRING" > /tmp/kre_record_set.json
    echo "It's going to be updated hosted zone with id ${hosted_zone_id} with the following content"
    cat /tmp/kre_record_set.json
    change_route_53_id=$(aws route53 change-resource-record-sets --hosted-zone-id ${hosted_zone_id} --change-batch file:///tmp/kre_record_set.json | jq -r '.ChangeInfo.Id')
    while [[ $(aws route53 get-change --id ${change_route_53_id}| jq -r '.ChangeInfo.Status') != "INSYNC" ]];
    do
        echo "Waiting until change in Route53 with id ${change_route_53_id} is propagated"
        sleep 5;
    done
    echo "Change in Route53 with id ${change_route_53_id} has INSYNC state"
}

function do_necessary_actions() {
    if [[ "$ACTION" == "-u" ]]; then
      wait_until_check_ingress_is_ready
    fi
    get_action_verb
    do_action_in_route53_record
}

function check_opts() {
  if [[ -z "${ACTION}" ]]; then
      echo "It's necessary provide ACTION as an argument"
      exit 1
  elif [[ "$ACTION" == "-u" || "$ACTION" == "-d" ]]; then
    do_necessary_actions
  else
      echo "Option not recognized, the only options available are u (update) and r (remove)"
  fi
}

check_opts
