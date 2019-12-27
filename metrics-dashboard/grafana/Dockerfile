FROM grafana/grafana:6.0.1

ENV GF_SECURITY_ADMIN_PASSWORD q1w2e3r4
ENV GF_INSTALL_PLUGINS=grafana-piechart-panel

USER 0
RUN apt-get update -y && apt-get install netcat -y
USER grafana
COPY metrics-dashboard/grafana/script.sh /tmp

COPY metrics-dashboard/grafana/datasources /etc/grafana/provisioning/datasources
COPY metrics-dashboard/grafana/dashboards /etc/grafana/provisioning/dashboards
COPY metrics-dashboard/grafana/dashboards-definitions /var/lib/grafana/dashboards

EXPOSE 3000