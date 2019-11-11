#!/bin/python
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO)

FNULL = open('/dev/null', 'w')


class CommonUtils:
    _default_wait_time_between_calls = 10
    _max_retries_call = 3

    def can_retry_call(self, call_try):
        if call_try <= self._max_retries_call:
            return True
        else:
            return False

    def retry_call(self, cmd_call, call_try):
        logging.info(
            f"Try number for call {call_try}: Waiting {self._default_wait_time_between_calls} seconds before try call "
            f"{cmd_call} again")
        call_result = subprocess.call(cmd_call.split(', '), stdout=FNULL)
        call_try += 1
        return call_result, call_try

    @staticmethod
    def check_current_state_call(current_state, aws_resource, aws_resource_name):
        if current_state == 0:
            logging.info("AWS resource {} with name {} was sucessfully removed".
                         format(aws_resource, aws_resource_name))
        else:
            logging.info("There where problems trying to delete AWS resource {} with name {}".
                         format(aws_resource, aws_resource_name))

