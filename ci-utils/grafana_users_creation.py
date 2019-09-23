#!/bin/python
import subprocess
import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
import asyncio
from sys import exit

_list = ["ENVIRONMENT_SLUG","GRAFANA_ADMIN_PASSWORD", "GRAFANA_ADMIN_USER", "GRAFANA_USER_EMAIL", 
"GRAFANA_USER_LOGIN", "GRAFANA_USER_NAME", "GRAFANA_USER_PASSWORD"]


def GetNecessaryVars(args):
    result = {"users": {}, "credentials": {}}
    environment_vars = os.environ
    result["credentials"] = { "ENVIRONMENT_SLUG": environment_vars.get("ENVIRONMENT_SLUG"),
                            "GRAFANA_ADMIN_USER": environment_vars.get("GRAFANA_ADMIN_USER"),
                            "GRAFANA_ADMIN_PASSWORD": environment_vars.get("GRAFANA_ADMIN_PASSWORD")}
    for i in args:
        if i not in ["GRAFANA_ADMIN_PASSWORD", "GRAFANA_ADMIN_USER", "ENVIRONMENT_SLUG"]:
            result["users"][i] = environment_vars.get(i)
            result["users"][i] = result["users"][i].split(",")
            result["users"][i] = [i.strip() for i in result["users"][i]]
    return result

def CheckUsersLength(users):
    n = []
    for k, v in users.items():
        n.append(len(v))
    check_in = True
    for i in n[1:]:
        if n[0] != i:
            check_in = False
        if check_in == False:
            break
    return check_in

def CheckIfUserExistsInGrafana(_list):
    result = GetNecessaryVars(_list)
    url_api_check_user = "https://admin:admin@{environment_slug}.mettel-automation.net/api/users/search?query={grafana_user_login}"
    environment_slug, grafana_admin_user, grafana_admin_password = result.get("credentials").values()
    users = result.get("users")
    if CheckUsersLength(users) == True:
        for i in users.get("GRAFANA_USER_LOGIN"):
            try:
                response = requests.get(url_api_check_user.format(environment_slug=environment_slug, grafana_user_login=i), 
                auth=HTTPBasicAuth(grafana_admin_user, grafana_admin_password))
                if (response.json().get("totalCount") == 0):
                    print("User {} doesn't exists yet in Grafana".format(i))
                    pos = users.get("GRAFANA_USER_LOGIN").index(i)
                    user = { k: v[pos] for k, v in users.items() }
                    user.update(result.get("credentials"))
                    UserCreationInGrafana(user)
                elif (response.json().get("totalCount") >= 1):
                    print("User {} already exists in Grafana".format(i))
                else:
                    print("Error searching user {} in Grafana".format(i))
            except ConnectionError as e:
                print(e)
                exit(1)


def UserCreationInGrafana(user):
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
    CheckIfUserExistsInGrafana(_list)