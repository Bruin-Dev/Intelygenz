#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open('/dev/null', 'w')


class S3Buckets:
    def delete_s3buckets(self, environment):
        logging.info("Checking if there are buckets related to the {} environment".format(environment))

    def _check_s3buckets_exists(self, environment):
        _s3_buckets_list = [f'terraform-{environment}-dev-resources.tfstate', f'terraform-{environment}-ecs-services.tfstate']
        for element in _s3_buckets_list:
            logging.info("Checking if s3 bucket with name {} exists".format(element))
