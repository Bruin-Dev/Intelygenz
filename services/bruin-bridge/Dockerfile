#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
ARG DOCKER_BASE_IMAGE_VERSION
FROM ${REPOSITORY_URL}/python-3.6-alpine:${DOCKER_BASE_IMAGE_VERSION}

COPY services/bruin-bridge/ /service/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

# This adds a certificate that is missing in the trust chain: DigiCert Global G2 TLS RSA SHA256 2020 CA1
# This certificate is mandatory to be able to log into Bruin
RUN cat digicert.crt >> $(python -m certifi)

CMD ["python3", "-u", "src/app.py"]

