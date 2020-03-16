#!/bin/python

import os
import json
import requests
from tenacity import retry, wait_exponential, stop_after_delay
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
from sys import exit
import time

ENV_SLUG = os.environ.get("ENVIRONMENT_SLUG")
GF_ADMIN = os.environ.get("GRAFANA_ADMIN_USER")
GF_PASS = os.environ.get("GRAFANA_ADMIN_PASSWORD")


def get_users():
    u_mails = os.environ.get("GRAFANA_USER_EMAIL").split(',')
    u_logins = os.environ.get("GRAFANA_USER_LOGIN").split(',')
    u_names = os.environ.get("GRAFANA_USER_NAME").split(',')
    u_passwords = os.environ.get("GRAFANA_USER_PASSWORD").split(',')
    u_roles = os.environ.get("GRAFANA_USER_ROLE").split(',')
    u_companies = os.environ.get("GRAFANA_USER_COMPANY").split(',')

    if not len(u_mails) == len(u_logins) == len(u_names) == len(u_passwords) == len(u_roles) == len(u_companies):
        print('User variables have different length; aborting process.')
        exit(1)

    users = []
    for i in range(len(u_names)):
        users.append(
            {
                'company': u_companies[i],
                'name': u_names[i],
                'email': u_mails[i],
                'login': u_logins[i],
                'password': u_passwords[i],
                'role': u_roles[i]
            }
        )
    return users


def check_users_existance():
    for u in get_users():
        try:
            response = requests.get(
                f'https://admin:admin@{ENV_SLUG}.'
                f'mettel-automation.net/api/users/search?'
                f'query={u["login"]}',
                auth=HTTPBasicAuth(GF_ADMIN, GF_PASS)
            )

            if response.json().get("totalCount") == 0:
                print(f'User {u["login"]} does not exist yet.')
                create_user(u)
            elif response.json().get("totalCount") >= 1:
                print(
                    f'User {u["login"]} already exists. '
                    f'ID: {response.json().get("users")[0]["id"]}'
                )
            else:
                print(response.text)
                print(f'Error searching for user {u["login"]}.')

        except ConnectionError as e:
            print(e)
            exit(1)

    update_main_folder_permissions()


@retry(wait=wait_exponential(multiplier=5,
                             min=5),
       stop=stop_after_delay(300))
def create_user(user):
    print(f'Creating user {user["login"]}.')
    user_data = {
        'name': user["name"],
        'email': user["email"],
        'login': user["login"],
        'password': user["password"]
    }

    try:
        response = requests.post(
            f'https://admin:admin@{ENV_SLUG}.'
            f'mettel-automation.net/api/admin/users',
            data=user_data,
            auth=HTTPBasicAuth(GF_ADMIN, GF_PASS)
        )
        if response.status_code == 200:
            print(f'Successfully created user {user["login"]}.')
            user_id = response.json().get("id")
            if user["role"] == 'editor':
                assign_editor_permissions(user, user_id)
            # user is a viewer
            else:
                assign_viewer_permissions(user, user_id)
        else:
            print(response.text)
            print(f'Error creating user {user["login"]}.')
            raise Exception
    except ConnectionError as e:
        print(e)
        exit(1)


@retry(wait=wait_exponential(multiplier=5,
                             min=5),
       stop=stop_after_delay(300))
def assign_viewer_permissions(user, user_id):

    user_data = {
        "items":
        [
            {
                "userId": user_id,
                "permission": 1
            },
            {
                "role": "Editor",
                "permission": 2
            }
        ]
    }
    folder_uid = get_folder_uid(user["company"])

    if folder_uid is None:
        print(f'Error updating permissions for user {user["login"]}.')
        raise Exception
    else:
        try:
            response = requests.post(
                f'https://admin:admin@{ENV_SLUG}.'
                f'mettel-automation.net/api/folders/'
                f'{folder_uid}/permissions',
                json=user_data,
                auth=HTTPBasicAuth(GF_ADMIN, GF_PASS)
            )

            if response.status_code == 200:
                print(f'Updated permissions for user {user["login"]}.')
            else:
                print(response.text)
                print(f'Error updating permissions for user {user["login"]}.')
                raise Exception
        except ConnectionError as e:
            print(e)
            exit(1)


@retry(wait=wait_exponential(multiplier=5,
                             min=5),
       stop=stop_after_delay(300))
def assign_editor_permissions(user, user_id):
    user_data = {"role": "Editor"}

    try:
        response = requests.patch(
            f'https://admin:admin@{ENV_SLUG}.'
            f'mettel-automation.net/api/org/users/{user_id}',
            json=user_data,
            auth=HTTPBasicAuth(GF_ADMIN, GF_PASS)
        )

        if response.status_code == 200:
            print(f'Updated permissions for user {user["login"]}.')
        else:
            print(response.text)
            print(f'Error updating permissions for user {user["login"]}.')
            raise Exception
    except ConnectionError as e:
        print(e)
        exit(1)


@retry(wait=wait_exponential(multiplier=5,
                             min=5),
       stop=stop_after_delay(300))
def get_folder_uid(user_company, main_folder=False):

    # Getting folder name
    if main_folder:
        folder_name = 'main'
    else:
        folder_name = user_company.split("|")[0].replace(" ", "-").lower()
    try:
        response = requests.get(
            f'https://admin:admin@{ENV_SLUG}.'
            f'mettel-automation.net/api/folders',
            auth=HTTPBasicAuth(GF_ADMIN, GF_PASS)
        )
        if response.status_code == 200:
            folders = response.json()
            for f in folders:
                if f["title"] == folder_name:
                    return f["uid"]
            print(f'There isn\'t a specific folder for the company {user_company}')
            return None
        else:
            raise Exception
    except ConnectionError as e:
        print(e)
        exit(1)


@retry(wait=wait_exponential(multiplier=5,
                             min=5),
       stop=stop_after_delay(300))
def update_main_folder_permissions():
    """
    Removes all permissions from main folder,
    meaning just admins or editors will see it.
    """
    main_data = {
        "items": [
            {
                "role": "Editor",
                "permission": 2
            }
        ]
    }
    main_folder_uid = get_folder_uid(None, True)

    if main_folder_uid is None:
        print(f'Error updating permissions of the main folder because it doesn\'t exists.')
        raise Exception
    else:
        try:
            response = requests.post(
                f'https://admin:admin@{ENV_SLUG}.'
                f'mettel-automation.net/api/folders/'
                f'{main_folder_uid}/permissions',
                json=main_data,
                auth=HTTPBasicAuth(GF_ADMIN, GF_PASS)
            )
            if response.status_code == 200:
                print(f'Updated permissions of the main folder.')
            else:
                print(response.text)
                print(f'Error updating permissions of the main folder.')
                raise Exception
        except ConnectionError as e:
            print(e)
            exit(1)


if __name__ == "__main__":
    check_users_existance()
