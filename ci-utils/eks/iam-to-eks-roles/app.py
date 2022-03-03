#!/usr/bin/env python3

import argparse
import boto3
import os
import json
import config
import kubernetes
from kubernetes import client
from sys import exit


class IamRolesUtil:
    # Configs can be set in Configuration class directly or using helper utility
    kubernetes.config.load_kube_config(
        os.path.join(os.environ["HOME"], '.kube/config'))
    _kubernetes_core_v1_api = client.CoreV1Api()
    _kubernetes_rbac_v1_api = client.RbacAuthorizationV1Api()

    def __init__(self):
        self._permission_assigned_to_roles = config.CLUSTER_ROLES_PERMISSIONS
        self._cluster_role_binding_config = config.CLUSTER_ROLE_BINDING_CONFIG

    @staticmethod
    def _get_necessary_botocore_session_data():
        aws_profile = parser.parse_args().aws_profile
        aws_region = parser.parse_args().aws_region

        aws_p = None
        aws_secret_access_key = None
        aws_acces_key_id = None

        if aws_profile:
            aws_p = aws_profile
        elif "AWS_PROFILE" in os.environ:
            aws_p = os.environ["AWS_PROFILE"]
        elif "AWS_SECRET_ACCESS_KEY" in os.environ and "AWS_ACCESS_KEY_ID" in os.environ:
            aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
            aws_acces_key_id = os.environ['AWS_ACCESS_KEY_ID']

        return aws_p, aws_secret_access_key, aws_acces_key_id, aws_region

    def _create_botocore_service_session(self, service_name):
        aws_profile, aws_secret_access_key, aws_acces_key_id, aws_region = self._get_necessary_botocore_session_data()
        if aws_profile:
            session = boto3.session.Session(profile_name=aws_profile)
        elif aws_secret_access_key and aws_acces_key_id:
            session = boto3.session.Session(aws_access_key_id=aws_acces_key_id,
                                            aws_secret_access_key=aws_secret_access_key)
        else:
            print("It's necessary provide valid AWS credentials")
            exit(1)
        return session.client(service_name, region_name=aws_region)

    @staticmethod
    def _get_necessary_attributes():
        project_tag = parser.parse_args().project_tag
        project_role_tag = parser.parse_args().project_role_tag
        project_env_tag = parser.parse_args().project_env_tag
        return project_tag, project_role_tag, project_env_tag

    @staticmethod
    def _create_necessary_tags_map(project_tag, project_role_tag, project_env_tag):
        if project_tag and project_role_tag:
            necessary_tags = [
                {
                    "Key": "Project",
                    "Value": project_tag
                },
                {
                    "Key": "Project-Role",
                    "Value": project_role_tag
                },
                {
                    "Key": "Project-Env",
                    "Value": project_env_tag
                }
            ]
            return necessary_tags
        else:
            print("It's necessary to provide a value for -p/--project-tag, --project-env-tag and --project-role-tag")
            exit(1)

    def _get_iam_roles_of_eks_with_specific_profile(self, iam_botocore_session, project, project_role, project_env):
        necessary_tags = self._create_necessary_tags_map(project, project_role, project_env)
        has_more_data = True
        marker = None
        roles_filtered = []
        print(f"Obtaining and filtering IAM roles for EKS users with {project_role} role in project {project}")
        while has_more_data:
            if marker:
                resp = iam_botocore_session.list_roles(
                    Marker=marker
                )
            else:
                resp = iam_botocore_session.list_roles()
            if not resp["Roles"]:
                break
            roles = resp["Roles"]
            for role in roles:
                rolename = role["RoleName"]
                role_arn = role["Arn"]
                role_tags = iam_botocore_session.list_role_tags(
                    RoleName=rolename
                )
                role_tags_l = role_tags["Tags"]
                if role_tags_l:
                    all_necessary_tags_in_role_tags = all(map(lambda tag: tag in role_tags_l, necessary_tags))
                    if all_necessary_tags_in_role_tags:
                        print(f"Role {rolename} satisfy tag conditions")
                        roles_filtered.append(
                            {
                                'role_name': rolename,
                                'role_arn': role_arn
                            }
                        )
            has_more_data = resp["IsTruncated"]
            if has_more_data:
                marker = resp["Marker"]
        return roles_filtered

    @staticmethod
    def _update_map_roles_items_aws_auth_cm(iam_roles_filtered, aws_auth_cm_map_roles):
        for iam_role in iam_roles_filtered:
            role_name = iam_role["role_name"]
            role_arn = iam_role["role_arn"]
            iam_role_to_add = (
                '- "groups": []\n'
                f'  "rolearn": "{role_arn}"\n'
                f'  "username": "{role_name}"\n'
            )
            if iam_role_to_add in aws_auth_cm_map_roles:
                print(f"User with name {role_name} and arn {role_arn} already presents in configmap")
            else:
                print(f"User with name {role_name} and arn {role_arn} not present in configmap yet, adding it")
                aws_auth_cm_map_roles += iam_role_to_add
        return aws_auth_cm_map_roles

    def _update_kubernetes_aws_auth_cm(self, iam_roles_filtered):
        print("Checking i configmap with name aws-auth exists")
        aws_auth_cm = self._kubernetes_core_v1_api.list_namespaced_config_map(
            namespace='kube-system',
            field_selector='metadata.name=aws-auth',
            watch=False,
            pretty='true'
        )
        if aws_auth_cm.items:
            print(f"ConfigMap with name aws-auth exists")

            aws_auth_cm_map_roles = aws_auth_cm.items[0].data['mapRoles']
            aws_auth_cm_map_roles_u = self._update_map_roles_items_aws_auth_cm(
                iam_roles_filtered,
                aws_auth_cm_map_roles)

            if aws_auth_cm_map_roles == aws_auth_cm_map_roles_u:
                print("It's not necessary update configmap aws-auth")
            else:
                aws_auth_cm.items[0].data['mapRoles'] = aws_auth_cm_map_roles_u
                print(f"It's going to update configmap mapRoles in aws-auth with the following")
                print(f"{aws_auth_cm_map_roles_u}")
                self._kubernetes_core_v1_api.replace_namespaced_config_map(
                    namespace='kube-system',
                    name='aws-auth',
                    body=aws_auth_cm.items[0]
                )
        else:
            print("Configmap aws-auth doesn't exists")
            exit(0)

    def _check_specific_cluster_role_exists(self, role_name):
        cluster_role_exists = False
        cluster_role = self._kubernetes_rbac_v1_api.list_cluster_role(
            field_selector='metadata.name=' + role_name,
            pretty='true'
        )
        if cluster_role.items:
            print(f"ClusterRole {role_name} already exists")
            cluster_role_exists = True
        else:
            print(f"Cluster {role_name} doesn't exists yet")
        return cluster_role_exists

    def _create_specific_cluster_role(self, role_name):
        cluster_roles_permissions_predefined = self._permission_assigned_to_roles
        role_permissions_are_defined = any(role_name in d for d in cluster_roles_permissions_predefined)
        if role_permissions_are_defined:
            cluster_role_permissions_rules = cluster_roles_permissions_predefined[role_name]['rules']
            cluster_role_api_version = cluster_roles_permissions_predefined[role_name]['apiVersion']
            print(f"Permissions for role {role_name} are predefined and are the following "
                  f"{cluster_roles_permissions_predefined}")
            body_create_role = {
                "kind": "ClusterRole",
                "apiVersion": cluster_role_api_version,
                "metadata": {
                    "name": role_name
                },
                "rules": cluster_role_permissions_rules
            }
            print(f"It's going to create a ClusterRole with name {role_name} with the following data")
            print(f"{json.dumps(body_create_role, indent=4, default=str)}")
            self._kubernetes_rbac_v1_api.create_cluster_role(body_create_role)

    def _check_specific_cluster_role_binding_exists(self, cluster_role_binding_name):
        cluster_role_binding = self._kubernetes_rbac_v1_api.list_cluster_role_binding(
            field_selector='metadata.name=' + cluster_role_binding_name,
            watch=False
        )
        cluster_role_binding_info = {
            'exists': False
        }
        if cluster_role_binding.items:
            print(f"ClusterRoleBinding {cluster_role_binding_name} already exists")
            cluster_role_binding_info.update(
                {
                    'exists': True,
                    'info': cluster_role_binding.items[0]
                }
            )
        else:
            print(f"ClusterRoleBinding {cluster_role_binding_name} doesn't exists yet")
        return cluster_role_binding_info

    def _generate_cluster_role_binding_body(self, role_name, cluster_role_binding_name, iam_roles_filtered):
        cluster_role_binding_config = self._cluster_role_binding_config
        role_ref_api_group = cluster_role_binding_config["roleRef"]["apiGroup"]
        role_subjects = [
            {
                'api_group': f'{role_ref_api_group}',
                'kind': 'User',
                'name': r["role_name"],
                'namespace': None
            } for r in iam_roles_filtered
        ]
        body_cluster_role_binding = {
            "apiVersion": f'{cluster_role_binding_config["apiVersion"]}',
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": cluster_role_binding_name
            },
            "subjects": role_subjects,
            "roleRef": {
                "kind": cluster_role_binding_config["roleRef"]["kind"],
                "name": role_name,
                "apiGroup": cluster_role_binding_config["roleRef"]["apiGroup"]
            }
        }
        return body_cluster_role_binding

    def _create_specific_cluster_role_binding(self, body_cluster_role_binding):
        cluster_role_binding_name = body_cluster_role_binding['metadata']['name']
        print(f"ClusterRoleBinding with name {cluster_role_binding_name} is going to be created "
              f"with the following content")
        print(f"{json.dumps(body_cluster_role_binding, indent=4, default=str)}")
        self._kubernetes_rbac_v1_api.create_cluster_role_binding(
            body=body_cluster_role_binding
        )

    @staticmethod
    def _convert_cluster_role_binding_subjects_without_v1_subjects_type(cluster_role_binding_subjects):
        cluster_role_binding_subjects_l = []
        for cluster_role_binding_subject in cluster_role_binding_subjects:
            cluster_role_binding_subjects_l.append(
                {
                    'api_group': cluster_role_binding_subject.api_group,
                    'kind': cluster_role_binding_subject.kind,
                    'name': cluster_role_binding_subject.name,
                    'namespace': cluster_role_binding_subject.namespace
                }
            )
        return cluster_role_binding_subjects_l

    def _update_specific_cluster_role_binding(self, body_cluster_role_binding, cluster_role_binding_info):
        cluster_role_binding_name = cluster_role_binding_info['info'].metadata.name

        print(f"It's going to check if is necessary update ClusterRoleBinding {cluster_role_binding_name}")

        body_cluster_role_binding_subjects = list(body_cluster_role_binding['subjects'])
        cluster_role_binding_actual_subjects = cluster_role_binding_info['info'].subjects
        cluster_role_binding_actual_subjects_l = self.\
            _convert_cluster_role_binding_subjects_without_v1_subjects_type(cluster_role_binding_actual_subjects)

        if body_cluster_role_binding_subjects == cluster_role_binding_actual_subjects_l:
            print(f"It's not necessary update ClusterRoleBinding with name {cluster_role_binding_name}")
        else:
            print(f"It's necessary update ClusterRoleBinding with name {cluster_role_binding_name} with the following")
            print(f"{json.dumps(body_cluster_role_binding, indent=4, default=str)}")
            self._kubernetes_rbac_v1_api.replace_cluster_role_binding(
                name=cluster_role_binding_name,
                body=body_cluster_role_binding
            )

    def do_necessary_actions(self):
        project, project_role, project_env = self._get_necessary_attributes()
        iam_botocore_session = self._create_botocore_service_session('iam')
        iam_roles_filtered = self._get_iam_roles_of_eks_with_specific_profile(iam_botocore_session,
                                                                              project,
                                                                              project_role,
                                                                              project_env)
        if iam_roles_filtered:
            self._update_kubernetes_aws_auth_cm(iam_roles_filtered)
            developer_cluster_role_exists = self._check_specific_cluster_role_exists(project_role)
            if not developer_cluster_role_exists:
                print(f"It's necessary to create ClusterRole with name {project_role}")
                self._create_specific_cluster_role(project_role)
            cluster_role_binding_name = project_role + "-performer"
            cluster_role_binding_info = self._check_specific_cluster_role_binding_exists(cluster_role_binding_name)
            cluster_role_binding_body_k8s = self._generate_cluster_role_binding_body(project_role,
                                                                                     cluster_role_binding_name,
                                                                                     iam_roles_filtered)
            if not cluster_role_binding_info['exists']:
                self._create_specific_cluster_role_binding(cluster_role_binding_body_k8s)
            else:
                self._update_specific_cluster_role_binding(cluster_role_binding_body_k8s,
                                                           cluster_role_binding_info)

        else:
            print("No IAM roles obtained that satisfy conditions")
            exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project-tag',
                        type=str,
                        help='Project tag to get users',
                        required=True)
    parser.add_argument('--project-role-tag',
                        type=str,
                        help='Project-Role tag to get users',
                        required=True)
    parser.add_argument('--project-env-tag',
                        type=str,
                        help='Project-Env tag to get users',
                        required=True)
    parser.add_argument('-a', '--aws-profile',
                        type=str,
                        help='AWS profile to use',
                        required=False)
    parser.add_argument('-r', '--aws-region',
                        type=str,
                        help='Region to use in AWS',
                        default='us-east-1',
                        required=False)
    iam_roles_util = IamRolesUtil()
    iam_roles_util.do_necessary_actions()
