#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM registry.gitlab.intelygenz.com/mettel/dockers/images/python3.10-alpine-base:1.0.0

RUN apk add gcc libffi-dev musl-dev git

RUN wget https://install.python-poetry.org -O poetry-install.py
RUN python poetry-install.py
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyutils_automation/py310 /pyutils_automation/py310
WORKDIR /pyutils_automation/py310
RUN poetry install --no-dev

COPY services/task-dispatcher/ /service/app
WORKDIR /service/app
RUN poetry install --no-dev

CMD ["python3", "-u", "src/app.py"]
