#NOTE: This dockerfile is made to be run with context in the root of the monorepo
FROM python:3.6

RUN pip install --upgrade pip
RUN pip install pandas==0.24.2

ENV PYTHONUNBUFFERED 1

COPY edge-monitoring-report/ /service/app
# Add custom packages to the image in order to import them
COPY custompackages/ /service/custompackages

WORKDIR /service/app

RUN pip install -r requirements.txt

CMD ["python3", "-u", "src/app.py"]
