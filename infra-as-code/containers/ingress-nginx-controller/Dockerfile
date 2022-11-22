#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM ubuntu:18.04

ARG NON_ROOT_USER=www-data
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
RUN useradd ${NON_ROOT_USER} --system --create-home --uid 1001 --gid 1001 && \
    chown ${NON_ROOT_USER}:${NON_ROOT_USER} /home/${NON_ROOT_USER}

# Set workdir to user home
WORKDIR /home/${NON_ROOT_USER}

# INSTALL RELOADER
RUN git clone --depth 1 --branch ${CONTAINER_VERSION} https://github.com/kubernetes/ingress-nginx.git

RUN cp -R ingress-nginx/rootfs/etc /etc
RUN cp -R ingress-nginx/rootfs/bin/${TARGETARCH}/dbg /
RUN cp -R ingress-nginx/rootfs/bin/${TARGETARCH}/nginx-ingress-controller /
RUN cp -R ingress-nginx/rootfs/bin/${TARGETARCH}/wait-shutdown /

RUN bash -xeu -c ' \
  writeDirs=( \
    /etc/ingress-controller \
    /etc/ingress-controller/ssl \
    /etc/ingress-controller/auth \
    /var/log \
    /var/log/nginx \
  ); \
  for dir in "${writeDirs[@]}"; do \
    mkdir -p ${dir}; \
    chown -R www-data.www-data ${dir}; \
  done'

RUN apk add --no-cache libcap \
  && setcap    cap_net_bind_service=+ep /nginx-ingress-controller \
  && setcap -v cap_net_bind_service=+ep /nginx-ingress-controller \
  && setcap    cap_net_bind_service=+ep /usr/local/nginx/sbin/nginx \
  && setcap -v cap_net_bind_service=+ep /usr/local/nginx/sbin/nginx \
  && setcap    cap_net_bind_service=+ep /usr/bin/dumb-init \
  && setcap -v cap_net_bind_service=+ep /usr/bin/dumb-init \
  && apk del libcap

RUN rm -rf ingress-nginx

# Use non-root user
USER ${NON_ROOT_USER}

# Create symlinks to redirect nginx logs to stdout and stderr docker log collector
RUN  ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD ["/nginx-ingress-controller"]