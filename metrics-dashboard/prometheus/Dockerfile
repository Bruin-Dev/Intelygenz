FROM prom/prometheus:v2.7.2

COPY metrics-dashboard/prometheus/prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090

CMD ["--config.file", "/etc/prometheus/prometheus.yml"]
