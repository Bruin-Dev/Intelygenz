#!/bin/python


import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
from sys import exit

_list = ["ENVIRONMENT_SLUG", "GRAFANA_ADMIN_PASSWORD", "GRAFANA_ADMIN_USER", "GRAFANA_USER_EMAIL",
         "GRAFANA_USER_LOGIN", "GRAFANA_USER_NAME", "GRAFANA_USER_PASSWORD"]


def get_necessary_vars(args):
    result = {"users": {}, "credentials": {}}
    environment_vars = os.environ
    result["credentials"] = {"ENVIRONMENT_SLUG": environment_vars.get("ENVIRONMENT_SLUG"),
                             "GRAFANA_ADMIN_USER": environment_vars.get("GRAFANA_ADMIN_USER"),
                             "GRAFANA_ADMIN_PASSWORD": environment_vars.get("GRAFANA_ADMIN_PASSWORD")}
    for i in args:
        if i not in ["GRAFANA_ADMIN_PASSWORD", "GRAFANA_ADMIN_USER", "ENVIRONMENT_SLUG"]:
            result["users"][i] = environment_vars.get(i)
            result["users"][i] = result["users"][i].split(",")
            result["users"][i] = [i.strip() for i in result["users"][i]]
    return result


def check_users_length(users):
    n = []
    for k, v in users.items():
        n.append(len(v))
    check_in = True
    for i in n[1:]:
        if n[0] != i:
            check_in = False
        if not check_in:
            break
    return check_in


def check_if_user_exists_in_grafana(_list):
    result = get_necessary_vars(_list)
    url_api_check_user = "https://admin:admin@{environment_slug}.mettel-automation.net/api/users/search?query={" \
                         "grafana_user_login} "
    environment_slug, grafana_admin_user, grafana_admin_password = result.get("credentials").values()
    users = result.get("users")
    if check_users_length(users):
        for i in users.get("GRAFANA_USER_LOGIN"):
            try:
                response = requests.get(
                    url_api_check_user.format(environment_slug=environment_slug, grafana_user_login=i),
                    auth=HTTPBasicAuth(grafana_admin_user, grafana_admin_password))
                if response.json().get("totalCount") == 0:
                    print("User {} doesn't exists yet in Grafana".format(i))
                    pos = users.get("GRAFANA_USER_LOGIN").index(i)
                    user = {k: v[pos] for k, v in users.items()}
                    user.update(result.get("credentials"))
                    user_creation_in_grafana(user)
                elif response.json().get("totalCount") >= 1:
                    print("User {} already exists in Grafana".format(i))
                else:
                    print("Error searching user {} in Grafana".format(i))
            except ConnectionError as e:
                print(e)
                exit(1)
    else:
        print("Not all the attributes necessary for the creation of users in Grafana are available")


def user_creation_in_grafana(user):
    url_api_create_user = "https://admin:admin@{environment_slug}.mettel-automation.net/api/admin/users"
    mapping = {"name": "GRAFANA_USER_NAME",
               "email": "GRAFANA_USER_EMAIL",
               "login": "GRAFANA_USER_LOGIN",
               "password": "GRAFANA_USER_PASSWORD"}
    data = {k: user.get(v) for k, v in mapping.items()}
    print("Creating user {} in Grafana".format(user.get("GRAFANA_USER_LOGIN")))
    try:
        response = requests.post(url_api_create_user.format(environment_slug=user.get("ENVIRONMENT_SLUG")), data=data,
                                 auth=HTTPBasicAuth(user.get("GRAFANA_ADMIN_USER"), user.get("GRAFANA_ADMIN_PASSWORD")))
        if response.status_code == 200:
            print("User {} successfully created in Grafana".format(user.get("GRAFANA_USER_LOGIN")))
        else:
            print("User {} not created in Grafana".format(user.get("GRAFANA_USER_LOGIN")))
    except ConnectionError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    check_if_user_exists_in_grafana(_list)
