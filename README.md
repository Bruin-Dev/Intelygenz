| Environment   | Status        |
|:-------------:|:-------------:|
| master        | [![pipeline status](https://gitlab.intelygenz.com/mettel/automation-engine/badges/master/pipeline.svg)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/master) |

| Module      | Coverage |
|:-----------:|:--------:|
| bruin-bridge |[![bruin-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=bruin-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| igzpackages |[![igzpackages-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=igzpackages-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| last-contact-report |[![last-contact-report-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=last-contact-report-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| notifier|[![notifier-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=notifier-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| service-affecting-monitor|[![service-affecting-monitor-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=service-affecting-monitor-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| service-outage-monitor|[![service-outage-monitor-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=service-outage-monitor-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| service-outage-triage|[![service-outage-triage-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=service-outage-triage-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| t7-bridge|[![t7-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=t7-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| velocloud-bridge|[![velocloud-bridge-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=velocloud-bridge-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| velocloud-orchestrator|[![velocloud-orchestrator-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=velocloud-orchestrator-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)
| velocloud|[![velocloud-test](https://gitlab.intelygenz.com/mettel/automation-engine/badges/dev/feature/add-new-environments-separation/coverage.svg?job=velocloud-test)](https://gitlab.intelygenz.com/mettel/automation-engine/commits/dev/feature/add-new-environments-separation)

# Table of Contents

- [Project structure](#project-structure)
  - [Naming conventions](#naming-conventions)
- [Technologies used](#technologies-used)
- [Developing flow](#developing-flow)
  - [DOD(Definition of Done)](#doddefinition-of-done)
  - [Custom packages](#custom-packages)
    - [Creation and testing](#creation-and-testing)
    - [Import and installation in microservices](#import-and-installation-in-microservices)
    - [Changes and debugging](#changes-and-debugging)
- [Run the project](#run-the-project)
- [Lists of projects READMEs](#lists-of-projects-readmes)
  - [Packages](#packages)
  - [Microservices](#microservices)
  - [Acceptance Tests](#acceptance-tests)
- [Processes' overview](#processes-overview)
  - [Monitoring edge and link status](#monitoring-edge-and-link-status)
    - [Process goal](#process-goal)
    - [Process flow](#process-flow)
- [Good Practices](#good-practices)
- [METRICS](#metrics)

# Project structure

## Naming conventions

- For folders containing services: kebab-case
- For a python package(directory): all lowercase, without underscores
- For a python module(file): all lowercase, with underscores only if improves readability.
- For a python class: should use CapsWord convention.
- Virtual env folders should be `project-name-env`. In case it is in a custom package as a user test environment 
it should be `package-example-env`

From [PEP-0008](https://www.python.org/dev/peps/pep-0008/#package-and-module-names)
Also check this, more synthesized [Python naming conventions](https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html) 

# Technologies used

- [Python 3.6](https://www.python.org/downloads/release/python-360/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Quart](http://pgjones.gitlab.io/quart/)
- [Quart OpenAPI](https://github.com/factset/quart-openapi)
- [Pytest](https://docs.pytest.org/en/latest/)
- [Behave](https://pypi.org/project/behave/)
- [Pip](https://pypi.org/project/pip/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)
- [Hypercorn to deploy Quart server](https://pgjones.gitlab.io/hypercorn/)
- [Requests for python HTTP requests](http://docs.python-requests.org/en/master/)
- [NATS (as event bus)](https://github.com/nats-io/nats-server)
- [Docker](https://www.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)
- [markdown-toc (for Table of Contents generation in READMEs)](https://github.com/jonschlinkert/markdown-toc)
- [PEP8 pre-commit hook](https://github.com/cbrueffer/pep8-git-hook) **MANDATORY**
- [AWS Fargate](https://aws.amazon.com/fargate/)

# Developing flow

- Create a branch from development
  
  - "feature" branches starts with feature/feature-name
  - "fix" branches starts with fix/issue-name

- When taking a fix or a feature, create a new branch. After first push to the remote repository, start a Merge Request with the title like the following: "WIP: your title goes here". That way, Maintainer and Approvers can read your changes while you develop them.
- **Remember that all code must have automated tests(unit and integration and must be part of an acceptance test) in it's pipeline.** 
- Assign that merge request to a any developer of the repository. Also add any affected developer as Approver. I.E: if you are developing a microservice wich is part of a process, you should add as Approvers both the developers of the first microservice ahead and the first behind in the process chain. Those microservices will be the more affected by your changes. 
- When a branch is merged into master, it will be deployed in production environment.
- When a new branch is created, it will be deployed in a new Fargate cluster. When a branch is deleted that cluster is deleted. **So every merge request should have "delete branch after merge"**
- You can also check in gitlab's project view, inside Operations>Environments, to see current running environments

## DOD(Definition of Done)

If any of the next requirements is not fulfilled in a merge request, merge request can't be merged. 

- Each service must have unit tests with a coverage percent of the 80% or more.
- Each service must have it's dockerfile and must be referenced in the docker-compose.
- Each service must have a linter job and a unit tests job in the gitlab.ci pipeline.
- If it is a new service, all the terraform code to deploy it should be present.
- Developers should take care of notify the devops/tech lead of putting in the pipeline env any environment variable needed in the pipeline's execution.

## Custom packages

Custom packages are developed using the same branching name and workflow that is used in other pieces of the project.
Custom packages are:
    - Wrappers of other packages to adapt them to our needs
    - SDKs or clients from 3rd party providers

Since they are going to be used among various microservices it is important not to duplicate their code, in order to ease the maintenance of them.

For the IDE to detect changes in custompackages, you need to uninstall & reinstall them via pip in your virtualenvs.

If changes are going to be persistent, remember to test them and change the version depending on the changes made. [Check semver](https://semver.org/) for that.

### Creation and testing

For a wrapper of other package (I.E: httpclient parametrized for some provider) test are **mandatory**.
If the package is a SDK provided by a 3rd party and will be used "as it is", no testing is needed.
If there are any new development to create a specific wrapper for an SDK provided, test are **mandatory** for that part.

To add an specific SDK for a 3rd party (I.E: VMWare's Velocloud), just add the SDK folder to the custompackages/ directory.

To add a wrapper for a library:
    - Create a package inside custompackages/igz/packages/ named mypackage
    - Create a test folder under custompackages/igz/tests/mypackage
    - Add your dependencies to custompackages/setup.py in the `REQUIRES` list.
    - Replicate file and folder structure in both folders.
    - Add config test variables under custompackages/igz/config/testconfig

### Import and installation in microservices

Add `../custompackages/packagename` to the microservice's requirements.txt file

Make sure the dockerfile copies the custompackages directory to the container.

**VERY IMPORTANT: If the microservice is using any custompackages, change any line related with them after each pip freeze for a relative import. I.E: If you are using velocloud package, change `velocloud==3.2.19` line to `../custompackages/velocloud`**

### Changes and debugging

If any change it's performed in a custom package, it must be uninstalled from the virtual environment and reinstalled with pip.

To debug with PyCharm, you must put the breakpoint **in the copy in site-packages** of the custompackage. To find that files, cntrl + right click on the in a call in your code of the function you want to debug.

# Run the project

`docker-compose up --build`

# Lists of projects READMEs

## Packages

- [Velocloud sdk](custompackages/velocloud/README.md)
- [IGZ packages](custompackages/igzpackages/README.md)

## Microservices

- [Base microservice](base-microservice/README.md)
- [Velocloud orchestrator](velocloud-orchestrator/README.md)
- [Velocloud bridge](velocloud-bridge/README.md)
- [Notifier](notifier/README.md)

## Acceptance Tests

- [Acceptance tests](acceptance-tests/README.md)

# Processes' overview

## Monitoring edge and link status

Services involved: velocloud-orchestrator, velocloud-bridge, notifier.

### Process goal

- Given an interval, process all edges and links statuses in that interval.
- Notify in a given channel. Just notify the faulty edges and a metric of it's statuses.

### Process flow

    - Orchestrator send a message to the Bridge through to ask for all edges given a list of Velocloud clusters.
    - For each edge it builds an event composed by the cluster's hostname, the edge ID and the company ID for that edge.
    - Publish events on NATS.
    - Orchestrator consumes the events from NATS and then send each edge to the NATS to be consumed by the Bridge.
    - For each event, it fetches the edge and link data related to the given IDs
    - Publishes edge and link data to NATS
    - Depending on the state of the edge, the Orchestrator will put the result event in a different Message Queue (one Queue for faulty edges, other for ok edges)
    - Notifier consumes the faulty edge queue and creates statistics. 
    - Notifier has an interval set. For each interval will send the statistics to a Slack channel and reset the statistics for the next cycle.

# Good Practices

- Documentation **must** be updated as frecuently as possible. It's recomended to annotate every action taken in the development phase, and afterwards, add to the documentation the actions or information considered relevant.
- Pair programming is strongly reccomended when doing difficult or delicate tasks. It is **mandatory** when a new teammate arrives.
- Solutions of hard problems should be put in common in order to use all the knowledge and points of view of the team.

# METRICS

- [Prometheus](http://localhost:9090) 
  - Github [link](https://github.com/prometheus/client_python) to documentation of Prometheus
  
  - Prometheus allows us to create counters/gauges in the velocloud-bridge to keep track of the metrics
    about edges processed in the bridge, amount of certain edges states found in the bridge, and amount of certain link states found in the bridge.
  
  - Using prometheus `start_http_server` we can host our metrics on a server. By using the file `prometheus.yml`located at
`/metrics-dashboard/prometheus/` and using the format below, you can add your server to the prometheus app. All the servers connected
to the prometheus app can be found at `http://localhost:9090/targets`.

- ```
    - job_name: <the microservice thats hosting you server>
        scrape_interval: 5s
        static_configs:
      - targets: [' <the microservice thats hosting you server>:<that server's port>'] 
  ```  

- [Grafana](http://localhost:3000) admin/q1w2e3r4

  - Grafana allows us to create graphs, tables, charts, and etc with the metrics created using Prometheus and other 
    default metrics.
  - [Link](https://prometheus.io/docs/prometheus/latest/querying/functions/) to functions you can use with your 
    Prometheus metrics in Grafana. 
  - You can run the Grafana server at `http://localhost:3000` using the credentials above.
  - In Grafana you can export a dashboard as a json file. By going to `metrics-dashboard/grafana/dashboard-definitions`
    you can add that json file to that folder and whenever the Grafana app is loaded up you can choose to make a new
    dashboard or use the dashboard that you created.  
  - [Link](https://grafana.com/docs/reference/dashboard/) to the documentation to the dashboard's json file.
  - The docker_compose should include the credentials above,specifically the password, in the`GF_SECURITY_ADMIN_PASSWORD` 
    area for the [local docker-compose](docker-compose.yml). Also the `GF_INSTALL_PLUGINS` field can be used to add any plugins you want to add to the
    grafana dashboard.
