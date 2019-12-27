import os
import subprocess
import json
import logging
import time
import sys
import re

logging.basicConfig(level=logging.INFO)

FNULL = open(os.devnull, 'w')
ENVIRONMENT = os.environ['TF_VAR_ENVIRONMENT']


class TaskHealthcheck:
    def check_task_is_ready(self, task_name_param):
        major_task_info = self._get_major_task(task_name_param)
        self._wait_until_task_is_ready(major_task_info, time.time())

    def _wait_until_task_is_ready(self, task_info, start_time):
        timeout = start_time + 60 * 6
        correct_exit = False
        actual_time = time.time()
        i = 1
        task_definition_arn = task_info['task_definition_arn']
        while timeout > actual_time:
            task_status = self._check_task_status(task_info)
            if task_status['task_is_running'] and task_status['task_is_healthy']:
                logging.info(f"Task {task_definition_arn} is RUNNING and with HEALTHY state")
                correct_exit = True
                break
            else:
                logging.info(f"Try {i}. Waiting for task {task_definition_arn}"
                             f" to be RUNNING and with HEALTHY state")
                time.sleep(30)
                actual_time = time.time()
                i += 1
        if actual_time > timeout and not correct_exit:
            logging.error(f"The maximum waiting time for {task_definition_arn} to be be RUNNING "
                          f"and with HEALTHY state has been reached")
            sys.exit(1)
        return correct_exit

    @staticmethod
    def _check_task_status(task_info):
        get_task_detail_call = subprocess.Popen(['aws', 'ecs', 'describe-tasks', '--cluster',
                                                 ENVIRONMENT, '--tasks', task_info['task_arn'], '--region',
                                                 'us-east-1'], stdout=subprocess.PIPE)
        get_task_detail_call_output = json.loads(get_task_detail_call.stdout.read())['tasks']
        if len(get_task_detail_call_output) > 0:
            task_is_running = False
            task_is_healthy = False
            task_info_detail = get_task_detail_call_output[0]
            if task_info_detail['lastStatus'] == "RUNNING":
                task_is_running = True
            if task_info_detail['healthStatus'] == "HEALTHY":
                task_is_healthy = True
            return {'task_is_running': task_is_running,
                    'task_is_healthy': task_is_healthy}
        else:
            logging.info(f"The task {task_info['task_arn']} doesn't exists")
            sys.exit(1)

    def _get_major_task(self, task_name_param):
        logging.info(f"Searching task with name {task_name_param} in the cluster ECS {ENVIRONMENT}")
        time.sleep(30)
        tasks_arn_with_task_name = self._get_tasks_arn_for_clusters(task_name_param)
        if tasks_arn_with_task_name is None:
            logging.error(f"No task running for specified task {task_name_param}")
            sys.exit(1)
        self._print_actual_tasks(task_name_param, tasks_arn_with_task_name)
        if len(tasks_arn_with_task_name) == 1:
            return tasks_arn_with_task_name[0]
        elif len(tasks_arn_with_task_name) > 1:
            tasks_arn_with_task_name.sort(key=lambda i: i['task_definition_arn'], reverse=True)
            return tasks_arn_with_task_name[0]

    @staticmethod
    def _print_actual_tasks(task_name_param, tasks_arn_with_task_name):
        logging.info(f"Actual tasks with name {task_name_param} are the following")
        for element in tasks_arn_with_task_name:
            logging.info(f"task_arn: {element['task_arn']}")
            logging.info(f"task_definition_arn: {element['task_definition_arn']}")

    @staticmethod
    def _get_tasks_arn_for_clusters(task_name_param):
        tasks_arn_call = subprocess.Popen(
            ['aws', 'ecs', 'list-tasks', '--cluster', ENVIRONMENT, '--region',
             'us-east-1'],
            stdout=subprocess.PIPE, stderr=FNULL)
        tasks_arn_list = json.loads(tasks_arn_call.stdout.read())['taskArns']
        container_arns = []
        for element in tasks_arn_list:
            get_task_detail_call = subprocess.Popen(['aws', 'ecs', 'describe-tasks', '--cluster',
                                                     ENVIRONMENT, '--tasks', element, '--region', 'us-east-1'],
                                                    stdout=subprocess.PIPE, stderr=FNULL)
            get_task_detail_call_output = json.loads(get_task_detail_call.stdout.read())['tasks']
            for i in range(len(get_task_detail_call_output[0]["containers"])):
                if task_name_param == get_task_detail_call_output[0]["containers"][i]["name"]:
                    container_arns.append({'task_arn': element,
                                           'task_definition_arn': get_task_detail_call_output[0]["taskDefinitionArn"]})
                    break
        return container_arns

    @staticmethod
    def print_usage():
        print('task_healthcheck.py -t <task_name>')


if __name__ == '__main__':
    task_healthcheck_instance = TaskHealthcheck()
    if sys.argv[0] == '-t':
        task_name = sys.argv[1]
    elif sys.argv[1] == '-t':
        task_name = sys.argv[2]
    else:
        task_healthcheck_instance.print_usage()
        sys.exit(1)

    task_healthcheck_instance.check_task_is_ready(task_name)
