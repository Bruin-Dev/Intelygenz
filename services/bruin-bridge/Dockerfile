#
# DEVELOPMENT DOCKERFILE
#
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM registry.gitlab.intelygenz.com/mettel/dockers/images/python3.10-base:1.0.0 AS DEVELOPMENT

ENV PYTHONUNBUFFERED 1
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

RUN wget https://install.python-poetry.org -O poetry-install.py
RUN python poetry-install.py

COPY pyutils_automation/py310 /pyutils_automation/py310
WORKDIR /pyutils_automation/py310
RUN poetry install --only main

COPY services/bruin-bridge/ /service/app
WORKDIR /service/app
RUN poetry install --only main

CMD ["python3", "-u", "src/app.py"]

#
# FEDRAMP DOCKERFILE
#
#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM ubuntu:18.04 AS FEDRAMP

# Input data
ARG NON_ROOT_USER=nroot
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1 \
    POETRY_VIRTUALENVS_CREATE=false

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Change to ROOT user to do maintenance/install tasks
USER root

# Working directory
WORKDIR /tmp

# Copy and install FIPS compliant cryptography packages
COPY /app/ubuntu18-fips/packages packages/

# Install Python 3.10 and configure as default
# DL3008 We won't pin versions here
# hadolint ignore=DL3008 ignore=DL3015
RUN apt-get update && \
    apt-get install --yes --quiet --no-install-recommends wget software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get --yes --quiet install python3.10 && \
    ln -s /usr/bin/python3.10 /usr/local/bin/python3 && \
    ln -s /usr/bin/python3.10 /usr/local/bin/python

# Install Poetry in a system-wide location
RUN wget -q https://install.python-poetry.org -O poetry-install.py && \
    POETRY_HOME=/usr/local python poetry-install.py

# Install FIPS compliant cryptography packages and clean
# hadolint ignore=DL3015 We want to install any extra FIPS packages
# hadolint ignore=DL3008 We won't pin versions of FIPS packages
RUN apt-get install --reinstall --yes --quiet ./packages/*.deb && \
    apt-get clean && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* ~/* && \
    rm -rf ./packages

# Create a non-root user
RUN groupadd ${NON_ROOT_USER} --gid 1001 && \
    useradd ${NON_ROOT_USER} --system --create-home --uid 1001 --gid 1001 && \
    chown ${NON_ROOT_USER}:${NON_ROOT_USER} /home/${NON_ROOT_USER}

# Use non-root user
USER ${NON_ROOT_USER}

# Set workdir to user home
WORKDIR /home/${NON_ROOT_USER}

# Copy utils and install with Poetry
COPY --chown=${NON_ROOT_USER}:0 pyutils_automation/py310 /home/${NON_ROOT_USER}/pyutils_automation/py310
WORKDIR /home/${NON_ROOT_USER}/pyutils_automation/py310
RUN poetry install --only main

COPY --chown=${NON_ROOT_USER}:0 /app/service /home/${NON_ROOT_USER}/app/service
WORKDIR /home/${NON_ROOT_USER}/app/service
RUN poetry install --only main

# Expose ports for the service
EXPOSE 5000 9090

# Run the service
CMD ["python3", "-u", "/app/src/app.py"]