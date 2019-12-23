FROM thanosio/thanos:v0.9.0

ARG GRPC_ADDRESS
ARG HTTP_ADDRESS

COPY metrics-dashboard/thanos/bucket_config.yaml /tmp

EXPOSE $GRPC_ADDRESS $HTTP_ADDRESS