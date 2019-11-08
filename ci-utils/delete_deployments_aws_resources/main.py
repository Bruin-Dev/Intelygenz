#!/bin/python


import sys
import getopt
import re
import logging

import ecs as ecs_module
import redis as redis_module
import alb as alb_module
import security_groups as security_groups_module
import metrics as metrics_module


logging.basicConfig(level=logging.INFO)


def _print_usage():
    print('main.py -e <environment> [-a] | [-c] [-d] [-r] [-l] [-s] [-m]')


def _delete_all(environment, ecs_instance, redis_instance, alb_instance, security_groups_instance, metrics_instance):
    logging.info("There are going to be deleted all AWS resources associated with the environment {}".format(environment))
    ecs_instance.delete_ecs_cluster(environment)
    redis_instance.delete_redis_cluster(environment)
    alb_instance.delete_alb(environment)
    security_groups_instance.delete_security_groups(environment)
    metrics_instance.delete_metrics_resources(environment)


if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "he:acdrlsm",
                                   ["environment=", "all", "ecs-cluster", "servicediscovery", "redis-cluster",
                                    "application-load-balancer",
                                    "security-groups", "metrics"])
    except getopt.GetoptError:
        _print_usage()
        sys.exit(2)

    delete_all = False
    if argv[0] != "-h" and (argv[0] != "-e" or re.match("-h|-a|-e|-d|-r|-l|-s|-m", argv[1])):
        _print_usage()
        sys.exit(2)
    elif "-a" or "--all" in argv[2:]:
        delete_all = True

    ecs_instance = ecs_module.EcsServices()
    redis_instance = redis_module.RedisCluster()
    alb_instance = alb_module.ApplicationLoadBalancer()
    security_groups_instance = security_groups_module.SecurityGroups()
    metrics_instance = metrics_module.Metrics()

    _, environment = opts.pop(0)
    if delete_all:
        _delete_all(environment, ecs_instance, redis_instance, alb_instance, security_groups_instance, metrics_instance)
        sys.exit(0)

    for opt, _ in opts:
        if opt == '-h':
            _print_usage()
            sys.exit()
        elif opt in ("-d", "--service-discovery"):
            ecs_instance.delete_servicediscovery(environment)
        elif opt in ("-c", "--ecs-cluster"):
            ecs_instance.delete_ecs_cluster(environment)
        elif opt in ("-r", "--redis-cluster"):
            redis_instance.delete_redis_cluster(environment)
        elif opt in ("-l", "--application-load-balancer"):
            alb_instance.delete_alb(environment)
        elif opt in ("-s", "--security-groups"):
            security_groups_instance.delete_security_groups(environment)
        elif opt in ("-m", "--metrics"):
            metrics_instance.delete_metrics_resources(environment)
