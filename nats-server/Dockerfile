FROM nats:2.1.0 

HEALTHCHECK --timeout=30s --interval=1m30s --retries=5 \
  CMD curl -s --fail http://localhost:8222/varz || exit 1

# Expose client and management ports
EXPOSE 4222 8222
