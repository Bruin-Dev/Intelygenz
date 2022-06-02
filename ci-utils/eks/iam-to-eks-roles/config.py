# In order to work, this module must be executed in an environment with the environment variables referenced set.
# use source env in this directory.
# If you dont have any env files, ask for one they are not in VCS
import os

CLUSTER_ROLES_PERMISSIONS = {
    "developer": {
        "rules": [
            {
                "apiGroups": [""],
                "resources": ["pods", "pods/log", "pods/exec", "configmaps", "secrets", "namespaces"],
                "verbs": ["get", "list", "watch", "create", "patch", "update", "delete"],
            },
            {
                "apiGroups": [""],
                "resources": [
                    "events",
                    "endpoints",
                    "namespaces",
                    "namespaces/finalize",
                    "namespaces/status",
                    "nodes",
                    "nodes/proxy",
                    "nodes/status",
                    "persistentvolumeclaims",
                    "persistentvolumeclaims/status",
                    "persistentvolumes",
                    "persistentvolumes/status",
                    "pods/attach",
                    "pods/binding",
                    "pods/eviction",
                    "pods/proxy",
                    "pods/status",
                    "serviceaccounts",
                    "services",
                    "services/proxy",
                    "services/status",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["apps"],
                "resources": [
                    "controllerrevisions",
                    "daemonsets",
                    "daemonsets/status",
                    "deployments",
                    "deployments/scale",
                    "deployments/status",
                    "replicasets",
                    "replicasets/scale",
                    "replicasets/status",
                    "statefulsets",
                    "statefulsets/scale",
                    "statefulsets/status",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["rbac.authorization.k8s.ioo"],
                "resources": ["clusterrolebindings", "clusterroles", "rolebindings", "roles"],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["extensions", "networking.k8s.io"],
                "resources": ["ingresses", "ingresses/status", "networkpolicies"],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["storage.k8s.io"],
                "resources": [
                    "csidrivers",
                    "csinodes",
                    "storageclasses",
                    "volumeattachments",
                    "volumeattachments/status",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {"apiGroups": ["scheduling.k8s.io"], "resources": ["priorityclasses"], "verbs": ["get", "list", "watch"]},
            {"apiGroups": ["metrics.k8s.io"], "resources": ["pods", "nodes"], "verbs": ["get", "list", "watch"]},
            {
                "apiGroups": ["events.k8s.io"],
                "resources": [
                    "events",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["apiextensions.k8s.io"],
                "resources": ["customresourcedefinitions", "customresourcedefinitions/status"],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["autoscaling"],
                "resources": ["horizontalpodautoscalers", "horizontalpodautoscalers/status"],
                "verbs": ["get", "list", "watch"],
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1",
    },
    "ops": {
        "rules": [
            {"apiGroups": ["", "apps"], "resources": ["*"], "verbs": ["*"]},
            {"apiGroups": ["external-secrets.io"], "resources": ["*"], "verbs": ["*"]},
            {
                "apiGroups": [""],
                "resources": [
                    "pods",
                    "pods/log",
                    "pods/exec",
                    "configmaps",
                    "secrets",
                    "namespaces",
                    "namespaces/finalize",
                    "namespaces/status",
                    "serviceaccounts",
                ],
                "verbs": ["*"],
            },
            {
                "apiGroups": [""],
                "resources": [
                    "nodes",
                    "nodes/proxy",
                    "nodes/status",
                    "persistentvolumeclaims",
                    "persistentvolumeclaims/status",
                    "persistentvolumes",
                    "persistentvolumes/status",
                    "pods/attach",
                    "pods/binding",
                    "pods/eviction",
                    "pods/proxy",
                    "pods/status",
                    "services",
                    "services/proxy",
                    "services/status",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["rbac.authorization.k8s.ioo"],
                "resources": ["clusterrolebindings", "clusterroles", "rolebindings", "roles"],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["extensions", "networking.k8s.io"],
                "resources": ["ingresses", "ingresses/status", "networkpolicies"],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["storage.k8s.io"],
                "resources": [
                    "csidrivers",
                    "csinodes",
                    "storageclasses",
                    "volumeattachments",
                    "volumeattachments/status",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {"apiGroups": ["scheduling.k8s.io"], "resources": ["priorityclasses"], "verbs": ["get", "list", "watch"]},
            {"apiGroups": ["metrics.k8s.io"], "resources": ["pods", "nodes"], "verbs": ["get", "list", "watch"]},
            {
                "apiGroups": ["events.k8s.io"],
                "resources": [
                    "events",
                ],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["apiextensions.k8s.io"],
                "resources": ["customresourcedefinitions", "customresourcedefinitions/status"],
                "verbs": ["get", "list", "watch"],
            },
            {
                "apiGroups": ["autoscaling"],
                "resources": ["horizontalpodautoscalers", "horizontalpodautoscalers/status"],
                "verbs": ["get", "list", "watch"],
            },
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1",
    },
    "devops": {
        "rules": [
            {"apiGroups": ["*"], "resources": ["*"], "verbs": ["*"]},
        ],
        "apiVersion": "rbac.authorization.k8s.io/v1",
    },
}

CLUSTER_ROLE_BINDING_CONFIG = {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "roleRef": {"apiGroup": "rbac.authorization.k8s.io", "kind": "ClusterRole"},
}
