#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}-python-3.6:${DOCKER_BASE_IMAGE_VERSION}

ENV PYTHONUNBUFFERED 1

COPY sites-monitor/ /service/app

RUN pip install -r requirements.txt --timeout=30

CMD ["python3", "-u", "src/app.py"]
