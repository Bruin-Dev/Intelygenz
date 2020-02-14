#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
FROM ${REPOSITORY_URL}-python-3.6:1.0.0

ENV PYTHONUNBUFFERED 1

COPY service-outage-triage/ /service/app

RUN pip install -r requirements.txt

CMD ["python3", "-u", "src/app.py"]
