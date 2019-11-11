#!/bin/python


import os
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class S3Buckets:
    def delete_s3buckets(self, environment):
        logging.info("Checking if there are buckets related to the {} environment".format(environment))

