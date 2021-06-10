#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}-python-3.6:${DOCKER_BASE_IMAGE_VERSION}


COPY ticket-collector/ /service/app

WORKDIR /service/app

RUN apt-get install -y wget
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]
