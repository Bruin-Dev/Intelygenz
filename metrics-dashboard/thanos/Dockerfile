FROM thanosio/thanos:v0.9.0

ARG GRPC_PORT
ARG HTTP_PORT

COPY metrics-dashboard/thanos/config/bucket_config.yaml /tmp
COPY metrics-dashboard/thanos/thanos-custom-entrypoint.sh /

RUN chmod +x /thanos-custom-entrypoint.sh
ENTRYPOINT [ "/thanos-custom-entrypoint.sh" ]

EXPOSE $GRPC_PORT $HTTP_PORT