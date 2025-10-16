FROM nexus3.onap.org:10001/onap/integration-python:12.0.0
# https://nexus3.onap.org/#browse/search=keyword%3Dintegration-python:d406d405e4cfbf1186265b01088caf9a
# https://git.onap.org/integration/docker/onap-python/tree/Dockerfile

USER root

ARG user=orano2
ARG group=orano2
# Create a group and user
RUN addgroup -S $group && adduser -S -D -h /home/$user $user $group && \
    chown -R $user:$group /home/$user &&  \
    mkdir /var/log/$user && \
    mkdir -p /src && \
    mkdir -p /configs/ && \
    mkdir -p /src/o2app/ && \
    mkdir -p /src/helm_sdk/ && \
    mkdir -p /etc/o2/ && \
    chown -R $user:$group /var/log/$user && \
    chown -R $user:$group /src && \
    chown -R $user:$group /configs && \
    chown -R $user:$group /etc/o2/

COPY requirements.txt /tmp/
COPY requirements-stx.txt /tmp/
COPY constraints.txt /tmp/


COPY o2ims/ /src/o2ims/
COPY o2dms/ /src/o2dms/
COPY o2common/ /src/o2common/
COPY o2app/ /src/o2app/
COPY setup.py /src/

<<<<<<< HEAD   (5dc7ba Merge "Fix the fault client returns 500 instend of 404" into)
=======
ENV PATH="/.venv/bin:${PATH}"

RUN mkdir -p /.venv && \
    python -m venv /.venv \
    && pip install --no-cache-dir --upgrade pip setuptools==78.1.1 \
    && pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements-stx.txt -c /tmp/constraints.txt \
    && pip install --no-cache-dir -e /src

FROM nexus3.onap.org:10001/onap/integration-python:12.0.0

ARG user=orano2
ARG group=orano2

USER root

# Upgrade packages to latest versions to mitigate CVEs
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    apk update \
    && apk add --upgrade expat busybox krb5 ncurses ncurses-dev sqlite sqlite-dev \
    && apk upgrade sqlite sqlite-dev --no-cache \
    && apk info expat busybox krb5 ncurses sqlite

RUN apk add --no-cache bash

COPY --from=build /.venv /.venv
COPY --from=build /src /src

# Create a group and user
RUN addgroup -S $group \
    && adduser -S -D -h /home/$user $user $group \
    && chown -R $user:$group /home/$user \
    && mkdir /var/log/$user \
    && mkdir -p /src \
    && mkdir -p /configs/ \
    && mkdir -p /src/o2app/ \
    && mkdir -p /src/helm_sdk/ \
    && mkdir -p /etc/o2/ \
    && chown -R $user:$group /var/log/$user \
    && chown -R $user:$group /src \
    && chown -R $user:$group /configs \
    && chown -R $user:$group /etc/o2/

>>>>>>> CHANGE (61595c Critical CVE resolution)
COPY helm_sdk/ /src/helm_sdk/

COPY configs/ /etc/o2/
COPY configs/ /configs/

RUN set -ex \
    && apk add --no-cache bash \
	&& apk add --no-cache --virtual .fetch2-deps \
        git curl \
    && apk add --no-cache --virtual .build2-deps  \
		bluez-dev \
		bzip2-dev \
		dpkg-dev dpkg \
		expat-dev \
		gcc \
		libc-dev \
		libffi-dev \
		libnsl-dev \
		libtirpc-dev \
		linux-headers \
		make \
		ncurses-dev \
		openssl-dev \
		pax-utils \
		sqlite-dev \
		tcl-dev \
		tk \
		tk-dev \
		util-linux-dev \
		xz-dev \
		zlib-dev \
    && pip install -r /tmp/requirements.txt -r /tmp/requirements-stx.txt -c /tmp/constraints.txt \
    && curl -O https://get.helm.sh/helm-v3.3.1-linux-amd64.tar.gz; \
        tar -zxvf helm-v3.3.1-linux-amd64.tar.gz; \
        cp linux-amd64/helm /usr/local/bin; \
        rm -f helm-v3.3.1-linux-amd64.tar.gz \
    && pip install -e /src \
    && apk del --no-network .fetch2-deps \
    && apk del --no-network .build2-deps

# && pip install -r /tmp/requirements.txt -r /tmp/requirements-stx.txt -c /tmp/constraints.txt
# RUN apt-get update && apt-get install -y git gcc procps vim curl ssh
# && git clone --depth 1 --branch r/stx.7.0 https://opendev.org/starlingx/config.git /cgtsclient \
# && git clone --depth 1 --branch r/stx.7.0 https://opendev.org/starlingx/distcloud-client.git /distcloud-client/ \
# && git clone --depth 1 --branch r/stx.7.0 https://opendev.org/starlingx/fault.git /faultclient \
# && pip install -e /cgtsclient/sysinv/cgts-client/cgts-client \
# && pip install -e /distcloud-client/distributedcloud-client \
# && pip install -e /faultclient/python-fmclient/fmclient \
# && rm -rf /cgtsclient /distcloud-client /faultclient

WORKDIR /src

# USER $user
ENV PYTHONHASHSEED=0
