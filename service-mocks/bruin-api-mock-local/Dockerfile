# note: This service is designed to run in local only
#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}/python-3.6-alpine:${DOCKER_BASE_IMAGE_VERSION}

COPY service-mock/bruin-api-mock-local/ /service/app

WORKDIR /service/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python", "-u", "src/app.py"]