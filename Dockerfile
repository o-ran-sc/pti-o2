FROM python:3.10-slim-buster

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY requirements-test.txt /tmp/
RUN pip install -r /tmp/requirements-test.txt

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src

COPY tests/ /tests/

WORKDIR /src
