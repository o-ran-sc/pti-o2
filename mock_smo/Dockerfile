FROM python:3.10-slim-buster

RUN apt-get update; apt-get install -y git gcc

COPY requirements.txt /tmp/
RUN  pip install -r /tmp/requirements.txt 

# COPY requirements-test.txt /tmp/
# RUN pip install -r /tmp/requirements-test.txt

RUN mkdir -p /src
COPY mock_smo/ /src/mock_smo/

COPY setup.py o2app-mock-smo.sh /src/
RUN pip install -e /src

COPY etc/ /etc/mock_smo/

# COPY tests/ /tests/

# RUN apt-get install -y procps vim

WORKDIR /src
