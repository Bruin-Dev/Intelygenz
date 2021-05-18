
<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

- [Technologies used](#technologies-used)
  * [Prerequisites:](#prerequisites-)
  * [Core](#core)
  * [Styles](#styles)
  * [Tests](#tests)
  * [Code quality](#code-quality)
  * [Other used libraries and their reason](#other-used-libraries-and-their-reason)
- [Developing flow](#developing-flow)
  * [DOD(Definition of Done)](#dod-definition-of-done-)
- [Project structure](#project-structure)
  * [Naming conventions](#naming-conventions)
  * [Scaffolding](#scaffolding)
  * [Work locally - check docker-compose](#work-locally---check-docker-compose)
  * [Work locally (Frontend)](#work-locally---frontend)
    + [1) With mocks:](#1--with-mocks-)
    + [2) Without mocks:](#2--without-mocks-)
    + [Open your terminal and browser:](#open-your-terminal-and-browser-)
  * [Environment variables management](#environment-variables-management)
  * [Test E2E](#test-e2e)
    + [For local](#for-local)
    + [For pipeline](#for-pipeline)
  * [Services and adapters](#services-and-adapters)
    + [Recomendations](#recomendations)
    + [API Documentation](#api-documentation)
    + [Mock management](#mock-management)
  * [Router](#router)
    + [Private routes](#private-routes)
  
  
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
- [Unit test, with react testing library](https://github.com/testing-library/react-testing-library), [jest-dom](https://github.com/testing-library/jest-dom) and [jest](https://jestjs.io/) √
- [E2E testing with Cypress.io](https://react-hook-form.com/) (not install yet, because at this moment it is impossible to test)

## Code quality
- [Eslint](https://eslint.org/) with [Wesbos config](https://github.com/wesbos/eslint-config-wesbos) and [Prettier](https://prettier.io/) √

## Other used libraries and their reason
- [Next Cookies](https://www.npmjs.com/package/next-cookies): Tiny little function for getting cookies on both client & server with next.js. This enables easy client-side and server-side rendering of pages that depend on cookies.
- [React-data-table-component](https://www.npmjs.com/package/react-data-table-component)
- [styled-components](https://styled-components.com/), only used to react data table.
- [axios-mock-adapter](https://www.npmjs.com/package/axios-mock-adapter) For init project mocks, Axios adapter that allows to easily mock requests.
- [tailwindcss](https://tailwindcss.com/docs) For css help.
- [debounce](https://www.npmjs.com/package/lodash.debounce) For search input.

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

## Scaffolding
- components/: Logic components.
- config/
    - constants/: constants folder.
    - config.js : to transform the process.env and global configuration
    - routes.js : file where we will be able to find all the path/routes available on the web, to avoid problems with literals and to be able to display the project in a subfolder.
- cypress/: to house the E2E tests, with their fixtures and steps.
- ningx/: configuration for deployment
- pages/: main project folder, business logic
- public/: Nextjs reserved folder, where we can host static files.
- services/:
    - example/: axios based service.
    - mocks/: where we mock up the services.
    - api.config.js: API config.
    - api.js: file where we make the logic to load mocks or not.
- ui/
    - components/: visual / dumb component folder
    - styles: global and variable styles in Sass
    
    
## Work locally - Check docker-compose
1) Start docker and the back images:
    ``docker-compose up --build redis nats-server lit-bridge cts-bridge dispatch-portal-frontend dispatch-portal-backend nginx bruin-bridge``

    Warning: and to login or renew the AWS token:
    ``echo $(aws ecr get-login-password --profile mettel)|docker login --password-stdin --username AWS 374050862540.dkr.ecr.us-east-1.amazonaws.com``
    
2) Navigate to the following address: 
    - http://localhost:8080/dispatch_portal/ (Real dispatch portal with Nginx)
    
    - http://localhost:5000/api/... (Api without Nginx)
    - http://localhost:3000 (Dispatch portal without Nginx, it does not work well, because it is configured to work with sub-routes (.../dispatch_portal/...))


## Work locally - frontend
Two scenarios:

### 1) With mocks:
Make sure you have activated the local environment with the mocks activated in file `next.config.js`:
```
// next.config.js
const currentEnv = process.env.CURRENT_ENV || ENVIRONMENTS.LOCAL; // default dev, for local development

const env = (() => {
  switch (currentEnv) {
    case ENVIRONMENTS.LOCAL:
      return {
        BASE_API: 'http://127.0.0.1:8080/dispatch_portal/api',
        BASE_PATH: '/',
        ENVIRONMENT: ENVIRONMENTS.LOCAL,
        MOCKS: true
      };
```
IMPORTANT: `MOCKS:true` and `const currentEnv = process.env.CURRENT_ENV || ENVIRONMENTS.LOCAL;`

### 2) Without mocks:
    - Start docker and the back images:
    ``docker-compose up --build redis nats-server lit-bridge cts-bridge dispatch-portal-frontend dispatch-portal-backend nginx bruin-bridge``

    - Warning: and to login or renew the AWS token:
    ``echo $(aws ecr get-login-password --profile mettel)|docker login --password-stdin --username AWS 374050862540.dkr.ecr.us-east-1.amazonaws.com``
    
    - Disable mocks in local environment, in file `next.config.js`:
    ```
    // next.config.js
    case ENVIRONMENTS.LOCAL:
          return {
            BASE_API: 'http://127.0.0.1:8080/dispatch_portal/api',
            BASE_PATH: '/',
            ENVIRONMENT: ENVIRONMENTS.LOCAL,
            MOCKS: false
          };
    ```
    
### Open your terminal and browser:
 `npm run dev` and open browser: `http://localhost:8081`


## Environment variables management
All variables go through two filters, or two steps:
    1) `next.config.js`: file where the environments and their variables are defined.
    2) `config/config.js`: we parsed the environment variables, to avoid their use with `process.env`

## Test E2E
### For local
We must have activated the mocks and two open terminals:
    1) Terminal 1: `npm run dev`, the project will be in port 8081
    2) Terminal 2: `npm run cy:open` or `npm run cy:run` 
    
### For pipeline
Everything is set up, so a compilation is done and then a start, with the help of the command: `npm run ci:test` 


## Services and adapters
All services are located inside the folder: `services/`

The idea is that each endpoint has its own folder and all services should follow the same pattern:
```js
// dispatch.service.js
export const dispatchService = {
  getAll: async () => {
    try {
      const res = await axiosInstance.get(API_URLS.DISPATCH);
      if (res.error) {
        return { error: res.error };
      }

      return {
        data: res.data.list_dispatch.map(dispatch =>
          dispatchLitInAdapter({ ...dispatch, vendor: res.data.vendor })
        )
      };
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  newDispatch: async data => {
    try {
      const res = await axiosInstance.post(
        API_URLS.DISPATCH,
        dispatchLitOutAdapter(data)
      );

      if (res.error) {
        return res.error;
      }

      return res;
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  get: async id => {
    try {
      const res = await axiosInstance.get(`${API_URLS.DISPATCH}/${id}`);

      if (res.error) {
        return res.error;
      }
      return dispatchLitInAdapter(res.data);
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  uploadFiles: async (id, data) => {
    try {
      const res = await axiosInstance.post(API_URLS.UPLOAD_FILES, data);

      if (res.error) {
        return false;
      }

      return true;
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  captureErrorGeneric: error => {
    if (error.response) {
      return { error };
    }
    if (error.request) {
    } else {
      console.log('Error', error.message);
    }
    console.log(error);
  }
};
```
The endpoints, their path, is defined in a configuration file called `api.config.js`
```
// api.config.js
export const API_URLS = {
  LOGIN: '/login',
  DISPATCH: '/lit/dispatch',
  UPLOAD_FILES: '/upload'
};
```

### Recomendations
- Inside the folder of each service, it is recommended to use adapters for data transformation.
- All services should use the following axios instance: `axiosInstance` obtained from the` api.js` file, this instance allows us to differentiate between mocks or real api.



### API Documentation
Link -> [http://localhost:5004/api/doc/](http://localhost:5004/api/doc/) before doing an `docker-compose up ...`


### Mock management
Inside the `services/` folder, we find the `mocks/` folder. In this folder we can easily mock our API, using the library [axios-mock-adapter](https://www.npmjs.com/package/axios-mock-adapter)
```
// mocks.js
mockadapter.onPost(API_URLS.LOGIN).reply(200, {
  token: 'XXXX-fake-token'
});
```

## Router
Router routes must be configured within the file: `config/routes.js`:
```
// routes.js
export const Routes = {
  BASE: () => `${config.basePath}`,
  DISPATCH: () => `${config.basePath}dispatch`,
  NEW_DISPATCH: () => `${config.basePath}new-dispatch`,
  LOGIN: () => `${config.basePath}login`
};
```


And we will use those routes as follows:
```
// menu.js
import { Routes } from '../../config/routes';

// ...

<div
    className={
      menuState
        ? `w-full block flex-grow lg:flex lg:items-center lg:w-auto`
        : `w-full hidden block flex-grow lg:flex lg:items-center lg:w-auto`
    }
    >
    <div className="text-sm lg:flex-grow">
      <a
        className="block mt-4 lg:inline-block lg:mt-0 text-teal-200 hover:text-white mr-4"
        href={Routes.BASE()}
      >
        Dashboard
      </a>
      <a
        className="block mt-4 lg:inline-block lg:mt-0 text-teal-200 hover:text-white mr-4"
        href={Routes.NEW_DISPATCH()}
      >
        New Dispatch
      </a>
    </div>
</div>    
// ...

```
Following this pattern, if we have to refactor/change the routes or deploy the project in a subfolder, this will be possible in a very simple way.


### Private routes
We can create private paths if we use the `components/privateRoute/PrivateRoute.js` component, this component uses the HOC pattern to read a cookie and do a redirect to login or not.

Example:
```
// pages/index.js
import { privateRoute } from '../components/privateRoute/PrivateRoute';

// ...
export default privateRoute(Index);
```

