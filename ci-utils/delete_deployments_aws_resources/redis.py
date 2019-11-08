#!/bin/python


import os
import subprocess
import json
import time
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class RedisCluster:
    @staticmethod
    def _check_redis_cluster_exists(environment):
        redis_cluster_exists = {}
        try:
            redis_cluster_call = subprocess.Popen(
                ['aws', 'elasticache', 'describe-cache-clusters', '--cache-cluster-id', environment, '--region',
                 'us-east-1'],
                stdout=subprocess.PIPE, stderr=FNULL)
            redis_cluster = json.loads(redis_cluster_call.stdout.read())
            if redis_cluster is not None:
                redis_cluster_exists.update({'exists': True, 'redis_cluster_information': redis_cluster})
        except ValueError as e:
            redis_cluster_exists.update({'exists': False})
        return redis_cluster_exists

    def _check_redis_cluster_is_deleted(self, environment, start_time):
        timeout = start_time + 60 * 5
        correct_exit = False
        actual_time = time.time()
        while timeout > actual_time:
            redis_cluster_status = self._check_redis_cluster_exists(environment)
            if redis_cluster_status['exists']:
                logging.info("Waiting for Redis cluster {} to be deleted".format(environment))
                logging.info("Time elapsed for delete Redis cluster {} seconds".format(actual_time - start_time))
                logging.info("Actual state of Redis cluster is: {}".format(
                    redis_cluster_status['redis_cluster_information']['CacheClusters'][0]['CacheClusterStatus']))
                time.sleep(30)
                actual_time = time.time()
            else:
                logging.info("Redis cluster {} has been deleted successfully".format(environment))
                correct_exit = True
                break
        if timeout > actual_time and not correct_exit:
            logging.error("The maximum waiting time for deleting the Redis cluster "
                          "{} (5 minutes) has elapsed and it has not been possible to delete it".format(environment))

    def delete_redis_cluster(self, environment):
        redis_cluster = self._check_redis_cluster_exists(environment)
        logging.info("Checking if there is a redis cluster related with the environment {}".format(environment))
        if redis_cluster['exists']:
            logging.info("There is a redis cluster related with environment exists and has {} cache nodes".
                         format(environment,redis_cluster['redis_cluster_information']['CacheClusters'][0]
                                                         ['NumCacheNodes']))
            logging.info("Redis cluster {} it's going to be deleted".format(environment))
            subprocess.call(
                ['aws', 'elasticache', 'delete-cache-cluster', '--cache-cluster-id', environment, '--region', 'us-east-1'],
                stdout=FNULL)
            start_time = time.time()
            self._check_redis_cluster_is_deleted(environment, start_time)
        else:
            logging.error("There isn't a redis cluster related with the environment {}".format(environment))
