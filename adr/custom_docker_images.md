# Custom Docker Images

## Date

03/06/2020

## State

ACCEPTED

## Context

The time required for the deployment of an environment in the project began to increase exponentially, as new microservices were added to the project.

After analysing the possible causes, it was concluded that the vast majority of the time of a deployment is consumed in the 'building' stage of a pipeline, in which the construction of the docker image of each of the microservices to be deployed in AWS in the 'deployment' phase is carried out.

Analyzing in more depth each one of the jobs of this stage, it was observed that they all started from a docker image `python:3.6` or `python:3.6-alpine`, installing a series of python libraries, a great set of them were installed in all the microservices, as well as the library created in a customized way for the project and called `igzpackages`.

## Decision

The decision was made to manage an external repository for the code used for the private igzpackages library, including semantic release in the repository to efficiently manage the version lifecycle.

In this external repository will also be included a module in charge of storing two Dockerfiles, these will start from the image of `python:3.6` and `python:3.6-alpine` respectively. A set of common python libraries will be installed, as well as a specific version of the `igzpackages` library, this will allow you to have a series of Python images with everything you need as base images for the Python microservices. These images will also be versioned using semantic-release.

In this external repository there will also be one more component where Dockerfiles will be stored to build custom images, these will be used in the different GitlabCI jobs of the project, avoiding having to install all the necessary software to execute the purpose of the job in each execution of it, which will allow a substantial time gain in the different jobs involved in a deployment.

## Consequences

### Positive

The positive consequences will be a notable improvement in the times of the different jobs of the CI/CD process, especially notable in those belonging to the build stage, where most of the time of this process is consumed.

#### Validation stage comparison

It's recomendable compare the difference between each job of `validation` stage for each module using the custom images and the previous method:

- *bruin-bridge*:
  - using custom image:
    - **Duration**: 33 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340283)
  - using old method:
    - **Duration**: 52 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341674)

- *ci-utils*:
  - using custom image:
    - **Duration**: 46 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340284)
  - using old method:
    - **Duration**: 50 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341675)

- *last-contact-report*:
  - using custom image:
    - **Duration**: 16 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340288)
  - using old method:
    - **Duration**: 53 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341680)

- *notifier*
  - using custom image:
    - **Duration**: 16 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340289)
  - using old method:
    - **Duration**: 1 minute 11 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341681)

- *notifications-bridge*
  - using custom image:
    - **Duration**: 16 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340289)
  - using old method:
    - **Duration**: 1 minute 11 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341681)

- *service-affecting-monitor*
  - using custom image:
    - **Duration**: 16 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340290)
  - using old method:
    - **Duration**: 1 minute 11 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341682)

- *service-outage-monitor*
  - using custom image:
    - **Duration**: 20 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340291)
  - using old method:
    - **Duration**: 1 minute 16 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341683)

- *t7-bridge*:
  - using custom image:
    - **Duration**: 15 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340293)
  - using old method:
    - **Duration**: 1 minute 11 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341684)

- *infra-as-code/basic-infra*:
  - using custom image:
    - **Duration**: 24 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340285)
  - using old method:
    - **Duration**: 52 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341677)

- *infra-as-code/dev*:
  - using custom image:
    - **Duration**: 52 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/3402875)
  - using old method:
    - **Duration**: 56 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341679)

- *infra-as-code/network-resources*:
  - using custom image:
    - **Duration**: 25 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340286)
  - using old method:
    - **Duration**: 54 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341678)

- *velocloud-bridge*
  - using custom image:
    - **Duration**: 16 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340294)
  - using old method:
    - **Duration**: 1 minute 17 seconds
    - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341685)

#### Unit_test stage comparison

It's recomendable compare the difference between each job of `unit_test` stage for each module using the custom images and the previous method:

- Microservices that will start from `python:3.6-alpine` image:

  - *bruin-bridge*:
    - using custom image:
      - **Duration**: 34 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340296)
    - using old method:
      - **Duration**: 1 minute 14 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334326)

  - *notifier*:
    - using custom image:
      - **Duration**: 30 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340298)
    - using old method:
      - **Duration**: 52 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334329)

  - *service-affecting-monitor*:
    - using custom image:
      - **Duration**: 29 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340299)
    - using old method:
      - **Duration**: 1 minute 6 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334330)

  - *velocloud-bridge*:
    - using custom image:
      - **Duration**: 30 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340303)
    - using old method:
      - **Duration**: 58 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334334)

- Microservices that will start from `python:3.6` image:

  - *last-contact-report*:
    - using custom image:
      - **Duration**: 19 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340297)
    - using old method:
      - **Duration**: 1 minute 10 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334328)

  - *service-outage-monitor*:
    - using custom image:
      - **Duration**: 19 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340300)
    - using old method:
      - **Duration**: 1 minute 5 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334331)

  - *service-outage-triage*:
    - using custom image:
      - **Duration**: 20 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340301)
    - using old method*
      - **Duration**: 1 minute 10 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334332)

  - *t7-bridge*:
    - using custom image:
      - **Duration**: 20 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340302)
    - using old method:
      - **Duration**: 1 minute 7 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/334333)

#### Build stage comparison

It’s recomendable compare the difference between each job of `build` stage for each image using the custom images and the previous method, making a differentiation according to the image from which they start:

- Microservices that will start from `python:3.6-alpine` image:

  - *bruin-bridge*:
    - using custom image:
      - **Duration**: 2 minutes 48 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340308)
    - using old method:
      - **Duration**: 5 minutes 8 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341700)

  - *notifier*:
    - using custom image:
      - **Duration**: 3 minutes 0 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340316)
    - using old method:
      - **Duration**: 5 minutes 25 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341708)

  - *notifications-bridge*:
    - using custom image:
      - **Duration**: 3 minutes 0 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340316)
    - using old method:
      - **Duration**: 5 minutes 25 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341708)

  - *service-affecting-monitor*:
    - using custom image:
      - **Duration**: 2 minutes 25 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340317)
    - using old method:
      - **Duration**: 5 minutes 53 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341709)

  - *velocloud-bridge*:
    - using custom image:
      - **Duration**: 3 minutes 27 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340321)
    - using old method:
      - **Duration**: 6 minutes 26 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341712)

- Microservices that will start from `python:3.6` image:

  - *last-contact-report*:
    - using custom image:
      - **Duration**: 5 minutes 6 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340309)
    - using old method:
      - **Duration**: 7 minutes 36 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341701)

  - *service-outage-monitor*:
    - using custom image:
      - **Duration**: 5 minutes 27 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340318)
    - using old method:
      - **Duration**: 9 minutes 44 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341468)

  - *service-outage-triage*:
    - using custom image:
      - **Duration**: 5 minutes 40 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340319)
    - using old method*
      - **Duration**: 12 minutes 9 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341469)

  - *t7-bridge*:
    - using custom image:
      - **Duration**: 5 minutes 52 seconds
      - [**GitlabCI job link**](hhttps://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/340320)
    - using old method:
      - **Duration**: 6 minutes 59 seconds
      - [**GitlabCI job link**](https://gitlab.intelygenz.com/mettel/automation-engine/-/jobs/341470)

### Negative

It becomes a little more complex to work on the project, since the following aspects about the images must be taken into account:

- The images published directly in [dockerhub](https://hub.docker.com/) will not be used as base images for the Dockerfile of the microservices, but private ones stored in the ECR repository used in the project.

- If you want to update the `igzpackages` library, you will need to update it in the specific repository where it will be managed, as well as update the variables to reference this library in the GitlabCI files so that it can be used in the CI/CD process.

-  Now that we are going to have an extra repo solely for the management of `custompackages` we have to deal with two MRs every time we need to carry out a feature or fix in `automation-engine` where altering code within this library is necessary. The MR in `custompackages` must be merged prior to the one in `automation-engine` in order to let the pipeline in the extra repo generate new Docker images and new version tags, which are needed to update `Dockerfile`s in `automation-engine`. It's a matter of coordinating actions.

  Fortunately, we won't have to change `custompackages` too much as this library holds common code across **all** the microservices of this system and hence this code is unlikely to change.

## Alternatives
