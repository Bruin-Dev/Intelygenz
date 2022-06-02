#!/bin/python


import getopt
import logging
import re
import sys

import alb as alb_module
import cloud_formation as cloud_formation_module
import ecs as ecs_module
import metrics as metrics_module
import redis as redis_module
import route53 as route53_module
import s3 as s3_module
import security_groups as security_groups_module

logging.basicConfig(level=logging.INFO)


def _print_usage():
    print("main.py -e <environment> [-a] | [-c] [-d] [-r] [-l] [-s] [-m] [-z] [-f] [-b]")


def _delete_all(
    environment,
    ecs_instance,
    redis_instance,
    alb_instance,
    security_groups_instance,
    metrics_instance,
    s3_instance,
    route53_instance,
    cloudformation_instance,
):
    logging.info(
        "There are going to be deleted all AWS resources associated with the environment {}".format(environment)
    )
    ecs_instance.delete_ecs_cluster(environment)
    redis_instance.delete_redis_resources(environment)
    alb_instance.delete_alb(environment)
    security_groups_instance.delete_security_groups(environment)
    metrics_instance.delete_metrics_resources(environment)
    route53_instance.delete_environment_record_set(environment)
    cloudformation_instance.delete_cloud_formation_resources(environment)
    s3_instance.delete_s3buckets(environment)


if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(
            argv,
            "he:acdrlsmbzf",
            [
                "environment=",
                "all",
                "ecs-cluster",
                "servicediscovery",
                "redis-cluster",
                "application-load-balancer",
                "security-groups",
                "metrics",
                "buckets",
                "hosted-zones",
                "cloud-formation",
            ],
        )
    except getopt.GetoptError:
        _print_usage()
        sys.exit(2)

    delete_all = False
    if argv[0] != "-h" and (argv[0] != "-e" or re.match("-h|-a|-e|-d|-r|-l|-s|-m|-b|-z|-f", argv[1])):
        _print_usage()
        sys.exit(2)
    elif "-a" in argv[2:] or "--all" in argv[2:]:
        delete_all = True

    ecs_instance = ecs_module.EcsServices()
    redis_instance = redis_module.RedisCluster()
    alb_instance = alb_module.ApplicationLoadBalancer()
    security_groups_instance = security_groups_module.SecurityGroups()
    metrics_instance = metrics_module.Metrics()
    s3_instance = s3_module.S3Buckets()
    route53_instance = route53_module.Route53()
    cloud_formation_instance = cloud_formation_module.CloudFormation()

    _, environment = opts.pop(0)
    if delete_all:
        _delete_all(
            environment,
            ecs_instance,
            redis_instance,
            alb_instance,
            security_groups_instance,
            metrics_instance,
            s3_instance,
            route53_instance,
            cloud_formation_instance,
        )
        sys.exit(0)

    for opt, _ in opts:
        if opt == "-h":
            _print_usage()
            sys.exit()
        elif opt in ("-d", "--service-discovery"):
            ecs_instance.delete_servicediscovery(environment)
        elif opt in ("-c", "--ecs-cluster"):
            ecs_instance.delete_ecs_cluster(environment)
        elif opt in ("-r", "--redis-cluster"):
            redis_instance.delete_redis_resources(environment)
        elif opt in ("-l", "--application-load-balancer"):
            alb_instance.delete_alb(environment)
        elif opt in ("-s", "--security-groups"):
            security_groups_instance.delete_security_groups(environment)
        elif opt in ("-m", "--metrics"):
            metrics_instance.delete_metrics_resources(environment)
        elif opt in ("-z", "--hosted-zones"):
            route53_instance.delete_environment_record_set(environment)
        elif opt in ("-f", "--cloud-formation"):
            cloud_formation_instance.delete_cloud_formation_resources(environment)
        elif opt in ("-b", "--buckets"):
            s3_instance.delete_s3buckets(environment)
