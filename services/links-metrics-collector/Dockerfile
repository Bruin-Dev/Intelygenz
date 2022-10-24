#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM registry.gitlab.intelygenz.com/mettel/dockers/images/python3.10-base:1.0.0

RUN wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem
RUN wget https://install.python-poetry.org -O poetry-install.py
RUN python poetry-install.py
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

COPY pyutils_automation/py310 /pyutils_automation/py310
WORKDIR /pyutils_automation/py310
RUN poetry install --only main

COPY services/links-metrics-collector/ /service/app
WORKDIR /service/app
RUN poetry install --only main

CMD ["python3", "-u", "src/app.py"]
