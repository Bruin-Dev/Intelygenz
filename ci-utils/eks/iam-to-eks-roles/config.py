# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os

CLUSTER_ROLES_PERMISSIONS = {
    "developer": {
        "rules": [
            {
                "apiGroups": [""],
                "resources": ["pods"],
                "verbs": ["get", "list", "watch"]
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1"
    },
    "developer-ops-privileged": {
        "rules": [
            {
                "apiGroups": ["", "apps"],
                "resources": ["*"],
                "verbs": ["*"]
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1"
    },
    "devops": {
        "rules": [
            {
                "apiGroups": ["*"],
                "resources": ["*"],
                "verbs": ["*"]
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1"
    }
}

CLUSTER_ROLE_BINDING_CONFIG = {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "roleRef": {
        "apiGroup": "rbac.authorization.k8s.io",
        "kind": "ClusterRole"
    }
}
