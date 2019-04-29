FROM scratch

COPY nats-streaming-server/nats-streaming-server /nats-streaming-server
COPY nats-streaming-server/nats.conf /nats.conf
# Expose client and management ports
EXPOSE 4222 8222

# Run with FILE based store and cluster mode. Details in nats.conf
ENTRYPOINT ["/nats-streaming-server"]
CMD ["-c", "/nats.conf"]
