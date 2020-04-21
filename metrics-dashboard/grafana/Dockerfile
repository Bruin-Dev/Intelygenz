FROM grafana/grafana:6.5.2

ARG IGZ_PACKAGES_REPOSITORY_URL
ARG IGZ_PACKAGES_VERSION
ENV IGZ_PACKAGES_VERSION=${IGZ_PACKAGES_VERSION}

USER root

ARG GRAFANA_ADMIN_PASSWORD
ARG GRAFANA_USER_PASSWORD
ENV GRAFANA_USER_PASSWORD=${GRAFANA_USER_PASSWORD}
ARG GRAFANA_ADMIN_USER
ENV GRAFANA_ADMIN_USER=${GRAFANA_ADMIN_USER}
ARG GRAFANA_USER_COMPANY
ENV GRAFANA_USER_COMPANY=${GRAFANA_USER_COMPANY}
ARG GRAFANA_USER_ROLE
ENV GRAFANA_USER_ROLE=${GRAFANA_USER_ROLE}
ARG GRAFANA_USER_NAME
ENV GRAFANA_USER_NAME=${GRAFANA_USER_NAME}
ARG GRAFANA_USER_LOGIN
ENV GRAFANA_USER_LOGIN=${GRAFANA_USER_LOGIN}
ARG GRAFANA_USER_EMAIL
ENV GRAFANA_USER_EMAIL=${GRAFANA_USER_EMAIL}
ARG GRAFANA_PORT
ENV GRAFANA_PORT=${GRAFANA_PORT}

ENV GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD
ENV GF_INSTALL_PLUGINS=grafana-piechart-panel

COPY ./metrics-dashboard /metrics-dashboard

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/main' >> /etc/apk/repositories
RUN apk update && apk add python3=3.6.9-r2 py3-setuptools gcc libc-dev g++ python3-dev musl-dev curl
RUN pip3 install -r /metrics-dashboard/grafana/requirements.txt

COPY metrics-dashboard/grafana/datasources /etc/grafana/provisioning/datasources
COPY metrics-dashboard/grafana/dashboards /etc/grafana/provisioning/dashboards
COPY metrics-dashboard/grafana/dashboards-definitions /var/lib/grafana/dashboards

COPY metrics-dashboard/grafana/grafana_entrypoint.sh /

EXPOSE 3000

RUN chmod +x /grafana_entrypoint.sh
ENTRYPOINT [ "/grafana_entrypoint.sh" ]
