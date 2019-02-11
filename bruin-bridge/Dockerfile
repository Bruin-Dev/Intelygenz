FROM python:3.6

COPY . /

RUN pip install pipenv

RUN pipenv install --system

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "app.py"]
