#!/bin/python


import sys
import getopt
import re

import alb as alb_module
import ecs as ecs_module
import metrics as metrics_module
import redis as redis_module
import security_groups as security_groups_module

if __name__ == "__main__":
    argv = sys.argv[1:]
    #import pdb; pdb.set_trace()
    try:
        opts, args = getopt.getopt(argv, "hc:derasm",
                                   ["cluster=", "servicediscovery", "ecs-cluster", "redis-cluster", "alb",
                                    "security-groups", "metrics"])
    except getopt.GetoptError:
        print('delete_deployments_resources.py -c <ecs_cluster_identifier> [-e] [-d] [-r] [-a] [-s] [-m]')
        sys.exit(2)

    if argv[0] != "-h" and (argv[0] != "-c" or re.match("-h|-e|-d|-r|-a|-s|-m", argv[1])):
        sys.exit(2)

    ecs_instances = ecs_module.EcsServices()
    for opt, arg in opts:
        if opt == '-h':
            print('delete_deployments_resources.py -c <ecs_cluster_identifier> [-e] [-d] [-r] [-a] [-s] [-m]')
            sys.exit()
        elif opt in ("-c", "--cluster"):
            cluster = arg
        elif opt in ("-d", "--service-discovery"):
            ecs_instances.delete_servicediscovery(cluster)
        elif opt in ("-e", "--ecs-cluster"):
            ecs_instances.delete_ecs_cluster(cluster)
        elif opt in ("-r", "--redis-cluster"):
            redis_module.delete_redis_cluster(cluster)
        elif opt in ("-a", "--alb"):
            alb_module.delete_alb(cluster)
        elif opt in ("-s", "--security-groups"):
            security_groups_module.delete_security_groups(cluster)
        elif opt in ("-m", "--metrics"):
            metrics_module.delete_metrics_resources(cluster)