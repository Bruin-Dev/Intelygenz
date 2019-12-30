FROM thanosio/thanos:v0.9.0

ARG GRPC_PORT
ARG HTTP_PORT

COPY metrics-dashboard/thanos/bucket_config.yaml /tmp

EXPOSE $GRPC_PORT $HTTP_PORT