#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM ubuntu:18.04

ARG NON_ROOT_USER=nroot
ARG CONTAINER_VERSION

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Working directory
WORKDIR /tmp

# Copy and install FIPS compliant cryptography packages
COPY ubuntu18-fips/packages packages/

# Install golang
RUN apt-get update -y -q && apt-get upgrade -y -q
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y -q curl build-essential ca-certificates git
RUN curl -s https://storage.googleapis.com/golang/go1.18.2.linux-amd64.tar.gz| tar -v -C /usr/local -xz
ENV PATH $PATH:/usr/local/go/bin

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

# INSTALL RELOADER
RUN git clone --depth 1 --branch ${CONTAINER_VERSION} https://github.com/kubernetes-sigs/metrics-server.git

RUN cp metrics-server/go.mod .
RUN cp metrics-server/go.sum . 
RUN cp -R metrics-server/pkg ./pkg 
RUN cp -R metrics-server/cmd ./cmd
RUN cp metrics-server/Makefile ./Makefile

RUN go mod download
RUN rm -rf metrics-server
RUN make metrics-server

RUN go build -o metrics-server main.go
RUN chmod g+rwX /home/nroot/metrics-server

ENTRYPOINT ["/home/nroot/metrics-server"]