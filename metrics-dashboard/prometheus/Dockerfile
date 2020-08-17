FROM prom/prometheus:v2.7.2

USER 0

RUN mkdir -p /thanos/store

COPY metrics-dashboard/prometheus/config/prometheus-dev.yml /etc/prometheus/prometheus.yml
COPY metrics-dashboard/prometheus/prometheus-custom-entrypoint.sh /

RUN chmod +x /prometheus-custom-entrypoint.sh
ENTRYPOINT [ "/prometheus-custom-entrypoint.sh" ]

EXPOSE 9090