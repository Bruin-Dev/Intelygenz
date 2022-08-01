#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM python:3.10-alpine

COPY integration-tests/ /service/app

WORKDIR /service/app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION='python'

CMD ["python", "-u", "src/app.py"]
