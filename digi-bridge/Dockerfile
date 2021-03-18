#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}-python-3.6-alpine:${DOCKER_BASE_IMAGE_VERSION}

RUN apk add bash

COPY digi-bridge/ /service/app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "/bin/bash", "-c", "./entrypoint.sh" ]