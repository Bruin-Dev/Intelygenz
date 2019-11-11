#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open('/dev/null', 'w')


class S3Buckets:
    _s3_bucket_backend = 'automation-infrastructure'

    def delete_s3buckets(self, environment):
        logging.info("Checking if there are directories in bucket {} related to the {} environment"
                     "for store Terraform tfstate files".format(self._s3_bucket_backend, environment))
        s3buckets_check = self._check_s3buckets_exists(environment)
        if s3buckets_check['s3_buckets']:
            logging.info("The environment {} has {} associated two directories to store Terraform state"
                         " that are going to be deleted".format(environment, len(s3buckets_check['buckets_list'])))
            for element in s3buckets_check['buckets_list']:
                logging.info("Removing directory {} from bucket {}".format(element, self._s3_bucket_backend))
                #subprocess.call(['aws', 's3', 'rm', element, '--region', 'us-east-1'], stdout=FNULL)
        else:
            logging.error("The environment {} hasn't any associated directories in bucket {} to store Terraform "
                          "state".format(environment, self._s3_bucket_backend))

    def _check_s3buckets_exists(self, environment):
        _has_s3_buckets = {'s3_buckets': False}
        _s3_buckets_list_to_check = [f's3://{self._s3_bucket_backend}/terraform-{environment}-dev-resources.tfstate',
                                     f's3://{self._s3_bucket_backend}/terraform-{environment}-ecs-services.tfstate']
        _s3_buckets_list_exists = []
        for element in _s3_buckets_list_to_check:
            logging.info("Checking if s3 bucket with name {} exists".format(element))
            s3_bucket_list_call = subprocess.Popen(['aws', 's3', 'ls', element], stdout=subprocess.PIPE,
                                                   stderr=FNULL)
            s3_bucket_list_call_result = s3_bucket_list_call.stdout.read().decode()
            if s3_bucket_list_call_result is not '':
                logging.info("Directory {} exists in bucket {}".format(element, self._s3_bucket_backend))
                _s3_buckets_list_exists.append(element)
            else:
                logging.error("Directory {} doesn't exists in bucket {}".format(element, self._s3_bucket_backend))
        if len(_s3_buckets_list_exists) > 0:
            _has_s3_buckets.update({'s3_buckets': True, 'buckets_list': _s3_buckets_list_exists})
        return _has_s3_buckets
