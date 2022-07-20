#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM python:3.6-alpine

RUN apk --no-cache add curl gcc musl-dev
RUN pip install --upgrade pip

COPY pyutils_automation/py36 /pyutils_automation/py36
WORKDIR /pyutils_automation/py36
RUN python setup.py install

COPY services/hawkeye-affecting-monitor/ /service/app
WORKDIR /service/app
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]