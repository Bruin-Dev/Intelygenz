# Table of Contents
- [Project structure](#project-structure)
  * [Naming conventions](#naming-conventions)
- [Technologies used](#technologies-used)
- [Developing flow](#developing-flow)
  * [Custom packages](#custom-packages)
    + [Creation and testing](#creation-and-testing)
    + [Import and installation in microservices](#import-and-installation-in-microservices)
    + [Changes and debugging](#changes-and-debugging)
- [Run the project](#run-the-project)
- [Lists of projects READMEs](#lists-of-projects-readmes)
  * [Packages](#packages)
  * [Microservices](#microservices)
  * [Acceptance Tests](#acceptance-tests)
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
 - [NATS(in streaming mode, as event bus)](https://nats.io/)
 - [Flask for APIs in Python](http://flask.pocoo.org/)
 - [Docker](https://www.docker.com/)
 - [Docker-compose](https://docs.docker.com/compose/)
 - [Kubernetes](https://kubernetes.io/)
 - [markdown-toc (for Table of Contents generation in READMEs)](https://github.com/jonschlinkert/markdown-toc)
 - [PEP8 pre-commit hook](https://github.com/cbrueffer/pep8-git-hook) **MANDATORY**
# Developing flow
- Create a branch from development
	- "feature" branches starts with feature/feature-name
	- "fix" branches starts with fix/issue-name
- When taking a fix or a feature, create a new branch. After first push to the remote repository, start a Merge Request with the title like the following: "WIP: your title goes here". That way, Maintainer and Approvers can read your changes while you develop them.
- **Remember that all code must have automated tests(unit and integration and must be part of an acceptance test) in it's pipeline.** 
- Assign that merge request to a Maintainer of the repository. Also add any affected developer as Approver. I.E: if you are developing a microservice wich is part of a process, you should add as Approvers both the developers of the first microservice ahead and the first behind in the process chain. Those microservices will be the more affected by your changes. 
- When deploying to production, a certain revision of the dev branch will be tagged. That will trigger all the pipelines needed to deploy.

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

## Acceptance Tests
- [Acceptance tests](acceptance-tests/README.md)

# Good Practices
- Documentation **must** be updated as frecuently as possible. It's recomended to annotate every action taken in the development phase, and afterwards, add to the documentation the actions or information considered relevant.
- Pair programming is strongly reccomended when doing difficult or delicate tasks. It is **mandatory** when a new teammate arrives.
- Solutions of hard problems should be put in common in order to use all the knowledge and points of view of the team.

# METRICS
- [Grafana](http://localhost:3000) admin/q1w2e3r4
