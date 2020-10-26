#!/usr/bin/env python3

import os
import subprocess
from sys import exit


class AddHelmRepositories:
    @staticmethod
    def _get_helm_repositories():
        if "HELM_CHART_REPOSITORIES" in os.environ:
            helm_chart_repos_l = os.environ.get("HELM_CHART_REPOSITORIES")
            return helm_chart_repos_l
        else:
            print("It's necessary export variable HELM_CHART_REPOSITORIES")
            exit(1)

    def add_helm_repositories(self):
        helm_repositories = self._get_helm_repositories()
        if helm_repositories:
            for repository in helm_repositories.split(", "):
                repository_name = repository.split(" ")[0]
                repository_url = repository.split(" ")[1]
                print(f"It's going to add helm repository with name {repository_name} and URL {repository_url}")
                subprocess.call(['helm', 'repo', 'add', repository_name, repository_url])


if __name__ == '__main__':
    add_helm_repositories = AddHelmRepositories()
    add_helm_repositories.add_helm_repositories()
