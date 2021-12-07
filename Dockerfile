FROM python:3.10-slim-buster

RUN apt-get update; apt-get install -y git gcc

# in case git repo is not accessable
# RUN mkdir -p /cgtsclient
# COPY temp/config /cgtsclient/
RUN git clone --depth 1 --branch master https://opendev.org/starlingx/config.git /cgtsclient
RUN pip install -e /cgtsclient/sysinv/cgts-client/cgts-client/

# RUN mkdir -p /distcloud-client
# COPY temp/distcloud-client /distcloud-client/
RUN git clone --depth 1 --branch master https://opendev.org/starlingx/distcloud-client.git /distcloud-client/
RUN pip install -e /distcloud-client/distributedcloud-client
# in case git repo is not accessable

# RUN git clone --depth 1 --branch master https://github.com/cloudify-incubator/cloudify-helm-plugin.git /helmsdk


COPY requirements.txt /tmp/
COPY requirements-stx.txt /tmp/
COPY constraints.txt /tmp/

RUN  pip install -r /tmp/requirements.txt -c /tmp/constraints.txt

# RUN  pip install -r /tmp/requirements-stx.txt

COPY requirements-test.txt /tmp/
RUN pip install -r /tmp/requirements-test.txt


RUN mkdir -p /src
COPY o2ims/ /src/o2ims/
COPY o2dms/ /src/o2dms/
COPY o2common/ /src/o2common/

RUN mkdir -p /src/o2app/
COPY o2app/ /src/o2app/
COPY setup.py /src/

RUN pip install -e /src

COPY configs/ /etc/o2/

COPY tests/ /tests/

RUN apt-get install -y procps vim

WORKDIR /src
