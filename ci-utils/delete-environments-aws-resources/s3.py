#!/bin/python


import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')


class S3Buckets:
    _s3_bucket_backend_terraform = 'automation-infrastructure'

    def delete_s3buckets(self, environment):
        self._delete_s3bucket_files_terraform_infrastructure(environment)
        self._delete_s3bucket_prometheus(environment)

    def _delete_s3bucket_prometheus(self, environment):
        bucket_prometheus = f'prometheus-storage-{environment}'
        s3_bucket_prometheus = f's3://prometheus-storage-{environment}'
        if self._check_s3_bucket_exists(s3_bucket_prometheus):
            if self._delete_content_of_bucket_recursively(s3_bucket_prometheus):
                logging.info(f"All contents of the bucket {bucket_prometheus} have been successfully deleted")
                if self._delete_s3_bucket(bucket_prometheus):
                    logging.info(f"S3 Bucket {bucket_prometheus} was successfully removed")
                else:
                    logging.error(f"There have been problems deleting S3 Bucket {bucket_prometheus}")
            else:
                logging.error(f"There have been problems deleting the contents of the bucket {bucket_prometheus}")

    def _delete_s3bucket_files_terraform_infrastructure(self, environment):
        logging.info(f"Checking if there are directories in s3 bucket {self._s3_bucket_backend_terraform} "
                     f"related to the {environment} environment for store Terraform tfstate files")
        s3buckets_check = self._check_s3_terraform_file_in_buckets_exists(environment)
        if s3buckets_check['s3_buckets']:
            logging.info(f"The environment {environment} has associated {len(s3buckets_check['buckets_list'])} "
                         f"directories to store Terraform state file "
                         f"that are going to be deleted")
            for element in s3buckets_check['buckets_list']:
                s3_directory_to_delete = f"s3://{element['bucket_name']}/{element['bucket_file']}"
                logging.info(f"Removing directory {element['bucket_file']} from s3 bucket {element['bucket_name']}")
                subprocess.call(['aws', 's3', 'rm', s3_directory_to_delete, '--region', 'us-east-1'], stdout=FNULL)
        else:
            logging.error("The environment {} hasn't any associated directories in bucket {} to store Terraform "
                          "state file".format(environment, self._s3_bucket_backend_terraform))

    def _check_s3_terraform_file_in_buckets_exists(self, environment):
        has_s3_buckets = {'s3_buckets': False}
        s3_buckets_list_to_check = [
            {
                "bucket_name": f"{self._s3_bucket_backend_terraform}",
                "bucket_file": f"terraform-{environment}-dev-resources.tfstate"
            }
        ]
        s3_buckets_list_exists = []
        for element in s3_buckets_list_to_check:
            if self._check_file_exists_in_s3_bucket(element['bucket_name'], element['bucket_file']):
                s3_buckets_list_exists.append(element)
        if len(s3_buckets_list_exists) > 0:
            has_s3_buckets.update({'s3_buckets': True, 'buckets_list': s3_buckets_list_exists})
        return has_s3_buckets

    @staticmethod
    def _check_file_exists_in_s3_bucket(bucket_name, file):
        s3_bucket_to_search = f"s3://{bucket_name}/{file}"
        logging.info(f"Checking if file {file} exists in S3 bucket {bucket_name}")
        s3_bucket_search_call = subprocess.Popen(['aws', 's3', 'ls', s3_bucket_to_search],
                                                 stdout=subprocess.PIPE,
                                                 stderr=FNULL)
        s3_bucket_search_call_result = s3_bucket_search_call.stdout.read().decode()
        if s3_bucket_search_call_result != '':
            logging.info(f"File {file} exists in S3 bucket {bucket_name}")
            return True
        logging.error(f"File {file} doesn't exists in S3 bucket {file}")
        return False

    @staticmethod
    def _check_s3_bucket_exists(bucket_name):
        command = ['aws', 's3', 'ls', bucket_name]
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
        if result.returncode != 0 and result.stderr != '':
            logging.error(f"S3 bucket {bucket_name} doesn't exists")
            return False
        logging.info(f"S3 Bucket {bucket_name} exists")
        return True

    @staticmethod
    def _delete_content_of_bucket_recursively(bucket_name):
        delete_bucket_result = subprocess.call(['aws', 's3', 'rm', bucket_name, '--recursive',
                                                '--region', 'us-east-1'], stdout=FNULL)
        if delete_bucket_result == 0:
            return True
        return False

    @staticmethod
    def _delete_s3_bucket(bucket_name):
        delete_bucket_result = subprocess.call(['aws', 's3api', 'delete-bucket', '--bucket', bucket_name,
                                                '--region', 'us-east-1'])
        if delete_bucket_result == 0:
            return True
        return False
