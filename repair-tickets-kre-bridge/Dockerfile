#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}-python-3.6:${DOCKER_BASE_IMAGE_VERSION}

COPY repair-ticket-kre-bridge/requirements.txt /service/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY repair-ticket-kre-bridge/ /service/app

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]
