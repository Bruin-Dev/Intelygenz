FROM python:3.6

COPY . /

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD ["python3", "-u", "src/app.py"]
