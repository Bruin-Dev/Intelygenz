#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM python:3.6

ARG acc_test
ARG json_file

ENV PYTHONUNBUFFERED 1
ENV ACC_TEST $acc_test
ENV BLUEPRINT $BLUEPRINT
ENV JSON_FILE $json_file

COPY acceptance-tests/ /service/acceptance-tests
COPY custompackages/ /service/custompackages

WORKDIR /service/

RUN apt-get update -q -y && apt install jq -y
RUN pip install --upgrade pip
RUN (cd acceptance-tests/$acc_test && pip install -r requirements.txt)

CMD (cd acceptance-tests/$ACC_TEST && behave src -f json -o results.json) && \
     python -u custompackages/igzpackages/igz/packages/honestcode/post_behave_result.py $JSON_FILE $BLUEPRINT

