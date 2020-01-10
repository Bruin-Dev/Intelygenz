FROM grafana/grafana:6.5.2

USER root

ARG GRAFANA_ADMIN_PASSWORD

ENV GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD
ENV GF_INSTALL_PLUGINS=grafana-piechart-panel

COPY custompackages/ mettel/custompackages/
COPY metrics-dashboard/grafana mettel/metrics-dashboard/grafana

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/main' >> /etc/apk/repositories
RUN apk update && apk add python3=3.6.9-r2 py3-setuptools gcc libc-dev g++ python3-dev
RUN pip3 install -r mettel/metrics-dashboard/grafana/requirements.txt

COPY ./custompackages /custompackages
COPY ./metrics-dashboard /metrics-dashboard

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/main' >> /etc/apk/repositories
RUN apk update && apk add python3=3.6.9-r2 py3-setuptools gcc libc-dev g++ python3-dev
RUN pip3 install -r /metrics-dashboard/grafana/requirements.txt

COPY metrics-dashboard/grafana/datasources /etc/grafana/provisioning/datasources
COPY metrics-dashboard/grafana/dashboards /etc/grafana/provisioning/dashboards
COPY metrics-dashboard/grafana/dashboards-definitions /var/lib/grafana/dashboards

COPY metrics-dashboard/grafana/grafana_entrypoint.sh /

EXPOSE 3000

RUN chmod +x /grafana_entrypoint.sh
ENTRYPOINT [ "/grafana_entrypoint.sh" ]
