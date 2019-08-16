FROM alpine

RUN apk add curl
HEALTHCHECK --timeout=30s --interval=1m30s --retries=5 \
  CMD curl -s --fail http://localhost:8222/streaming/serverz || exit 1

COPY nats-streaming-server/nats-streaming-server /nats-streaming-server
COPY nats-streaming-server/nats.conf /nats.conf
# Expose client and management ports
EXPOSE 4222 8222

# Run with FILE based store and cluster mode. Details in nats.conf
ENTRYPOINT ["/nats-streaming-server"]
CMD ["-c", "/nats.conf"]
