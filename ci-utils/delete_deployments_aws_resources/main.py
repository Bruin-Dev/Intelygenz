#!/bin/python


import sys
import getopt
import re

import ecs as ecs_module
import redis as redis_module
import alb as alb_module
import security_groups as security_groups_module
import metrics as metrics_module


def _usage():
    print('main.py -e <environment> [-c] [-d] [-r] [-l] [-s] [-m]')


if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "he:cdrlsm",
                                   ["environment=", "servicediscovery", "ecs-cluster", "redis-cluster",
                                    "application-load-balancer",
                                    "security-groups", "metrics"])
    except getopt.GetoptError:
        _usage()
        sys.exit(2)

    if argv[0] != "-h" and (argv[0] != "-e" or re.match("-h|-e|-d|-r|-l|-s|-m", argv[1])):
        _usage()
        sys.exit(2)

    ecs_instances = ecs_module.EcsServices()
    redis_instance = redis_module.RedisCluster()
    alb_instance = alb_module.ApplicationLoadBalancer()
    security_groups_instance = security_groups_module.SecurityGroups()
    metrics_instance = metrics_module.Metrics()

    for opt, arg in opts:
        if opt == '-h':
            _usage()
            sys.exit()
        elif opt in ("-e", "--environment"):
            environment = arg
        elif opt in ("-d", "--service-discovery"):
            ecs_instances.delete_servicediscovery(environment)
        elif opt in ("-c", "--ecs-cluster"):
            ecs_instances.delete_ecs_cluster(environment)
        elif opt in ("-r", "--redis-cluster"):
            redis_instance.delete_redis_cluster(environment)
        elif opt in ("-l", "--application-load-balancer"):
            alb_instance.delete_alb(environment)
        elif opt in ("-s", "--security-groups"):
            security_groups_instance.delete_security_groups(environment)
        elif opt in ("-m", "--metrics"):
            metrics_instance.delete_metrics_resources(environment)
