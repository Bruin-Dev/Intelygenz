#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM ubuntu:18.04

# Input data
ARG NON_ROOT_USER=nroot
# ARG REPOSITORY_URL
# ARG DOCKER_BASE_IMAGE_VERSION
ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1 \
    POETRY_VIRTUALENVS_CREATE=false

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Change to ROOT user to do maintenance/install tasks
USER root

# Working directory
WORKDIR /tmp

# Copy and install FIPS compliant cryptography packages
COPY ubuntu18-fips/packages packages/

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
    rm -rf /var/lib/apt/lists/* /tmp/* ~/* %&& \
    rm -rf ./packages

# Create a non-root user
RUN groupadd ${NON_ROOT_USER} --gid 1001 && \
    useradd ${NON_ROOT_USER} --system --create-home --uid 1001 --gid 1001 && \
    chown ${NON_ROOT_USER}:${NON_ROOT_USER} /home/${NON_ROOT_USER}

# Use non-root user
USER ${NON_ROOT_USER}

# Set workdir to user home
WORKDIR /home/${NON_ROOT_USER}

COPY --chown=${NON_ROOT_USER}:0 pyutils_automation/py310 /pyutils_automation/py310
WORKDIR /pyutils_automation/py310
RUN poetry install --no-dev

COPY --chown=${NON_ROOT_USER}:0 services/notifications-bridge/ /service/app
WORKDIR /service/app
RUN poetry install --no-dev

EXPOSE 5000 9090

CMD ["python3", "-u", "src/app.py"]
