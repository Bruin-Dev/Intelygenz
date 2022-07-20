#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM python:3.6

RUN apt-get update -y
RUN apt-get install -y curl gcc musl-dev
RUN pip install --upgrade pip
RUN wget https://grpcio-certs.s3.amazonaws.com/root-certificates.txt -O /tmp/root-certificates.txt

COPY pyutils_automation/py36 /pyutils_automation/py36
WORKDIR /pyutils_automation/py36
RUN python setup.py install

COPY services/email-tagger-kre-bridge/ /service/app
WORKDIR /service/app
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]

