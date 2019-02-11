# Table of Contents
- [Project structure](#project-structure)
  * [Naming conventions](#naming-conventions)
  * [Root of the project](#root-of-the-project)
- [Technologies used](#technologies-used)
- [Developing flow](#developing-flow)
- [Run the project](#run-the-project)
- [Good Practices](#good-practices)

# Project structure
## Naming conventions
- For folders: kebab-case
## Root of the project
- New service: new folder with a project within.

# Technologies used
 - [Python 3.6](https://www.python.org/downloads/release/python-360/)
 - [NATS(in streaming mode, as event bus)](https://nats.io/)
 - [Flask for APIs in Python](http://flask.pocoo.org/)
 - [Docker](https://www.docker.com/)
 - [Docker-compose](https://docs.docker.com/compose/)
 - [Kubernetes](https://kubernetes.io/)
 - [markdown-toc (for Table of Contents generation in READMEs)](https://github.com/jonschlinkert/markdown-toc)
# Developing flow
- Create a branch from development
	- "feature" branches starts with feature/feature-name
	- "fix" branches starts with fix/issue-name
- When taking a fix or a feature, create a new branch. After first push to the remote repository, start a Merge Request with the title like the following: "WIP: your title goes here". That way, Maintainer and Approvers can read your changes while you develop them.
- **Remember that all code must have automated tests(unit and integration and must be part of an acceptance test) in it's pipeline.** 
- Assign that merge request to a Maintainer of the repository. Also add any affected developer as Approver. I.E: if you are developing a microservice wich is part of a process, you should add as Approvers both the developers of the first microservice ahead and the first behind in the process chain. Those microservices will be the more affected by your changes. 
- When deploying to production, a certain revision of the dev branch will be tagged. That will trigger all the pipelines needed to deploy.

# Run the project
````
docker-compose up --build
````

# Good Practices
- Documentation **must** be updated as frecuently as possible. It's recomended to annotate every action taken in the development phase, and afterwards, add to the documentation the actions or information considered relevant.
- Pair programming is strongly reccomended when doing difficult or delicate tasks. It is **mandatory** when a new teammate arrives.
- Solutions of hard problems should be put in common in order to use all the knowledge and points of view of the team.
