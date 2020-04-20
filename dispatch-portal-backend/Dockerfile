#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}-python-3.6:${DOCKER_BASE_IMAGE_VERSION}

RUN pip install --upgrade pip
COPY dispatch-portal-backend/requirements.txt /service/app/requirements.txt
RUN pip install -r requirements.txt

COPY dispatch-portal-backend/ /service/app

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]
