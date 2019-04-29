FROM prom/prometheus:v2.7.2

ENV GF_SECURITY_ADMIN_PASSWORD q1w2e3r4

COPY metrics-dashboard/prometheus/prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090

CMD ["--config.file", "/etc/prometheus/prometheus.yml"]
