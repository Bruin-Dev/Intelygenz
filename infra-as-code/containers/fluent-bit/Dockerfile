#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM ubuntu:18.04 AS FEDRAMP

ARG NON_ROOT_USER=nroot
# Fluent Bit version; update these for each release
ARG FLB_VERSION 1.7.6
# branch to pull parsers from in github.com/fluent/fluent-bit-docker-image
ARG FLB_DOCKER_BRANCH 1.7

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
RUN apt-get --yes install libseccomp-dev && \
    apt-get install --reinstall --yes --quiet ./packages/*.deb && \
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

RUN git clone https://github.com/fluent/fluent-bit.git /tmp/fluent-bit-$FLB_VERSION/
WORKDIR /tmp/fluent-bit-$FLB_VERSION/build/
RUN git fetch --all --tags && git checkout tags/v${FLB_VERSION} -b v${FLB_VERSION} && git describe --tags
RUN cmake -DFLB_DEBUG=On \
          -DFLB_TRACE=Off \
          -DFLB_JEMALLOC=On \
          -DFLB_TLS=On \
          -DFLB_SHARED_LIB=Off \
          -DFLB_EXAMPLES=Off \
          -DFLB_HTTP_SERVER=On \
          -DFLB_IN_SYSTEMD=On \
          -DFLB_OUT_KAFKA=On ..

RUN make -j $(getconf _NPROCESSORS_ONLN)
RUN install bin/fluent-bit /fluent-bit/bin/

# Configuration files
COPY fluent-bit.conf \
     /fluent-bit/etc/

# Add parsers files
WORKDIR /home
RUN git clone https://github.com/fluent/fluent-bit-docker-image.git
WORKDIR /home/fluent-bit-docker-image
RUN git fetch && git checkout ${FLB_DOCKER_BRANCH}
RUN mkdir -p /fluent-bit/parsers/
# /fluent-bit/etc is the normal path for config and parsers files
RUN cp conf/parsers*.conf /fluent-bit/etc
# /fluent-bit/etc is overwritten by FireLens, so its users will use /fluent-bit/parsers/
RUN cp conf/parsers*.conf /fluent-bit/parsers/

ADD configs/parse-json.conf /fluent-bit/configs/
ADD configs/minimize-log-loss.conf /fluent-bit/configs/

COPY --from=builder /fluent-bit /fluent-bit
COPY --from=aws-fluent-bit-plugins:latest /kinesis-streams/bin/kinesis.so /fluent-bit/kinesis.so
COPY --from=aws-fluent-bit-plugins:latest /kinesis-firehose/bin/firehose.so /fluent-bit/firehose.so
COPY --from=aws-fluent-bit-plugins:latest /cloudwatch/bin/cloudwatch.so /fluent-bit/cloudwatch.so
RUN mkdir -p /fluent-bit/licenses/fluent-bit
RUN mkdir -p /fluent-bit/licenses/firehose
RUN mkdir -p /fluent-bit/licenses/cloudwatch
RUN mkdir -p /fluent-bit/licenses/kinesis
COPY THIRD-PARTY /fluent-bit/licenses/fluent-bit/
COPY --from=aws-fluent-bit-plugins:latest /kinesis-firehose/THIRD-PARTY \
    /kinesis-firehose/LICENSE \
    /fluent-bit/licenses/firehose/
COPY --from=aws-fluent-bit-plugins:latest /cloudwatch/THIRD-PARTY \
    /cloudwatch/LICENSE \
    /fluent-bit/licenses/cloudwatch/
COPY --from=aws-fluent-bit-plugins:latest /kinesis-streams/THIRD-PARTY \
    /kinesis-streams/LICENSE \
    /fluent-bit/licenses/kinesis/
COPY AWS_FOR_FLUENT_BIT_VERSION /AWS_FOR_FLUENT_BIT_VERSION
ADD ecs /ecs/

CMD exec /fluent-bit/bin/fluent-bit -e /fluent-bit/firehose.so -e /fluent-bit/cloudwatch.so -e /fluent-bit/kinesis.so -c /fluent-bit/etc/fluent-bit.conf /bin/bash
