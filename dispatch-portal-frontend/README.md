
<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# Project structure

## Naming conventions

- For folders containing services: kebab-case
- Filename: Use PascalCase for filenames. E.g., ReservationCard.jsx.
- Reference Naming: Use PascalCase for React components and camelCase for their instances.
- Component Naming: Use the filename as the component name.
- Variable and function names written as camelCase
- Global variables written in UPPERCASE (We don't, but it's quite common)
- Constants (like PI) written in UPPERCASE

Also check this, more synthesized [Naming conventions Airbnb react](https://github.com/airbnb/javascript/tree/master/react#naming) 

# Technologies used
## Prerequisites:
To launch the application you need first install some mandatory dependencies.

At the time of writing this document we are using the following global versions:

| --          | Nodejs    | NPM        |
| --          | --         | --        |
| **Version** | **10.19.0** | **>=6.13.4** |


## Core
- [React](https://es.reactjs.org/) + [NextJS](https://nextjs.org/). √
- Data validator, [prop-types](https://www.npmjs.com/package/prop-types) √
- [Forms: with react hook form](https://react-hook-form.com/) √
- Fetch, with [Axios](https://github.com/axios/axios) √
- Extras:
    - [i18n](https://www.i18next.com/) X (not install yet)
     
## Styles
- [Sass](https://sass-lang.com/), Without css-modules. √
- [Storybooks](https://storybook.js.org/), lib for ui-components. √

## Tests
- [Unit test, with react testing library](https://github.com/testing-library/react-testing-library) √
- [E2E testing with Cypress.io](https://react-hook-form.com/) (not install yet, because at this moment it is impossible to test)

## Code quality
- [Eslint](https://eslint.org/) with [Wesbos config](https://github.com/wesbos/eslint-config-wesbos) and [Prettier](https://prettier.io/) √

## Other used libraries and their reason
- [Next Cookies](https://www.npmjs.com/package/next-cookies): Tiny little function for getting cookies on both client & server with next.js. This enables easy client-side and server-side rendering of pages that depend on cookies.
- [React-data-table-component](https://www.npmjs.com/package/react-data-table-component)
- [styled-components](https://styled-components.com/), only used to react data table.
- [axios-mock-adapter](https://www.npmjs.com/package/axios-mock-adapter) For init project mocks, Axios adapter that allows to easily mock requests.
- [tailwindcss](https://tailwindcss.com/docs) For css help.

# Developing flow

- Create a branch from development
  - "feature" branches starts with `feature/<feature-name>` or `dev/feature/<feature-name>`
  - "fix" branches starts with `fix/<issue-name>` or `dev/fix/<issue-name>`

  Branches whose name begins with `dev/feature/<feature-name>` or `dev/fix/issue-name` will perform both [CI](docs/PIPELINES.md#continuous-integration-ci) and [CD](docs/PIPELINES.md#continuous-delivery-cd) processing, while those whose name begins with `feature-<feature-name>` or `fix-<issue-name>` will perform only [CI](docs/PIPELINES.md#continuous-integration-ci) processing.

  >It is strongly recommended to always start with a `feature/<feature-name>` or `fix/<issue-name>` branch, and once the development is ready, rename it to `dev/feature/<feature-name>` or `dev/fix/<issue-name>` and push this changes to the repository.

- When taking a fix or a feature, create a new branch. After first push to the remote repository, start a Merge Request with the title like the following: "WIP: your title goes here". That way, Maintainer and Approvers can read your changes while you develop them.
- **Remember that all code must have automated tests(unit and integration and must be part of an acceptance test) in it's pipeline.** 
- Assign that merge request to a any developer of the repository. Also add any affected developer as Approver. I.E: if you are developing a microservice wich is part of a process, you should add as Approvers both the developers of the first microservice ahead and the first behind in the process chain. Those microservices will be the more affected by your changes. 
- When a branch is merged into master, it will be deployed in production environment.
- When a new branch is created, it will be deployed in a new Fargate cluster. When a branch is deleted that cluster is deleted. **So every merge request should have "delete branch after merge"**
- You can also check in gitlab's project view, inside Operations>Environments, to see current running environments.

## DOD(Definition of Done)

If any of the next requirements is not fulfilled in a merge request, merge request can't be merged. 

- Must have unit tests with a coverage percent of the 80% or more.
- Must have it's dockerfile and must be referenced in the docker-compose.
- Must have a linter job and a unit tests job in the gitlab.ci pipeline.
- Developers should take care of notify the devops/tech lead of putting in the pipeline env any environment variable needed in the pipeline's execution.


## Work locally

Start docker and the back images:
``docker-compose up --build redis nats-server lit-bridge cts-bridge dispatch-portal-backend nginx bruin-bridge``

and to login or renew the AWS token:
``echo $(aws ecr get-login-password --profile mettel)|docker login --password-stdin --username AWS 374050862540.dkr.ecr.us-east-1.amazonaws.com``
