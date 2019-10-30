FROM nats:2.1.0-alpine3.10

RUN apk --no-cache add curl bash net-tools

COPY /nats-server/nats.sh .
CMD ["/bin/bash", "./nats.sh"]

HEALTHCHECK --timeout=30s --interval=1m30s --retries=5 \
  CMD curl -s --fail http://localhost:8222/varz || exit 1