#NOTE: This dockerfile is made to be run with context in the root of the monorepo
ARG REPOSITORY_URL
FROM ${REPOSITORY_URL}-python-3.6:1.0.0

COPY last-contact-report/ /service/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]
