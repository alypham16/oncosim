FROM python:3.12

COPY . /code

WORKDIR /code

RUN pip install -- no-cache-dir -r requirements.txt