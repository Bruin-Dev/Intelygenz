# ADR

**Table of contents**:

- [Introduction](#introduction)
- [How to use ADRs in repository](#how-to-use-adrs-in-repository)
  - [ADR format](#adr-format)
- [Actual ADRs](#actual-adrs)
  - [Custom Docker Images](#custom-docker-images)

## Introduction

> An architecture decision record (ADR) is a document that captures an important architectural decision made along with its context and consequences.
> [joelparkerhenderson](https://github.com/joelparkerhenderson/architecture_decision_record#what-is-an-architecture-decision-record)

## How to use ADRs in repository

There is an `adr` folder in the root of the repository, in which the different ADRs made for technical decisions made in the project will be stored.

To create a new ADR, simply create a file with a markdown extension in that folder, using a meaningful name for the change, and separating the words between `_`. For example: `choose_database.md`

### ADR format

There is a [template document](adr_template.md) that can be used as a basis for generating new ADRs. Each ADR will have a number of sections that will need to be fully completed once the technical decision is fully implemented, these are outlined below.

- **Title**: Title of the ADR

- **Date**: Date of last modification on the ADR.

- **State**: ADR state, which may be any of the following: *PROPOSED*, *ACCEPTED*, *REJECTED*, *OBSOLET* or *REPLACED*

- **Context**: What is the issue that we're seeing that is motivating this decision or change?

- **Decision**: Clearly state the architecture’s direction—that is, the position you’ve selected.

- **Consequences**: What becomes easier or more difficult to do because of this change?
  The consequences are divided into two sections:

  - **Positive**: Positive consequences of making the technical decision, such as: improvement in deployment time, optimization of transactions, etc.
  
  - **Negative**: Negative consequences of making the technical decision, such as: increased code complexity, increased transactions per second, etc.

- **Alternatives**: List the positions (viable options or alternatives) you considered. These often require long explanations, sometimes even models and diagrams. This isn’t an exhaustive list. However, you don’t want to hear the question "Did you think about...?" during a final review; this leads to loss of credibility and questioning of other architectural decisions. This section also helps ensure that you heard others’ opinions; explicitly stating other opinions helps enroll their advocates in your decision.

## Actual ADRs

Current ADRs are presented in the following sections

### Custom Docker Images

The ADR [Custom Docker Images](./custom_docker_images.md) explains the use of custom docker images in the Dockerfile of the different Python microservices present in the project.