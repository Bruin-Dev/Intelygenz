#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM ubuntu:18.04 AS FEDRAMP

ARG NON_ROOT_USER=nroot
ARG CONTAINER_VERSION=v0.0.103

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Working directory
WORKDIR /tmp

# Copy and install FIPS compliant cryptography packages
COPY /app/ubuntu18-fips/packages packages/

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
RUN git clone --depth 1 --branch ${CONTAINER_VERSION} https://github.com/stakater/Reloader.git

RUN cp Reloader/main.go .
RUN cp Reloader/go.mod .
RUN cp Reloader/go.sum . 
RUN cp -R Reloader/internal ./internal
RUN cp -R Reloader/pkg ./pkg

RUN go mod download
RUN rm -rf Reloader

RUN CGO_ENABLED=0 \
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH} \
    GOPROXY=${GOPROXY} \
    GOPRIVATE=${GOPRIVATE} \
    GO111MODULE=on \
    go build -mod=mod -a -o manager main.go

EXPOSE 9090

ENTRYPOINT ["/home/nroot/manager"]