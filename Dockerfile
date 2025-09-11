FROM python:3.12-slim

RUN mkdir -p /opt/app

ADD ./requirements.txt /opt/app

WORKDIR /opt/app

RUN pip install -r requirements.txt

ADD . /opt/app/

EXPOSE 8000
