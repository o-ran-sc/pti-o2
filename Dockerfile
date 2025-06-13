FROM nexus3.onap.org:10001/onap/integration-python:12.0.0 as build
# https://nexus3.onap.org/#browse/search=keyword%3Dintegration-python:d406d405e4cfbf1186265b01088caf9a
# https://git.onap.org/integration/docker/onap-python/tree/Dockerfile

USER root

RUN apk add --no-cache \
    git \
    curl \
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
    openssl-dev \
    pax-utils \
    tcl-dev \
    tk \
    tk-dev \
    util-linux-dev \
    xz-dev \
    zlib-dev \
    && curl -O https://get.helm.sh/helm-v3.3.1-linux-amd64.tar.gz \
    && tar -zxvf helm-v3.3.1-linux-amd64.tar.gz \
    && cp linux-amd64/helm /usr/local/bin \
    && rm -f helm-v3.3.1-linux-amd64.tar.gz

COPY requirements.txt /tmp/
COPY requirements-stx.txt /tmp/
COPY constraints.txt /tmp/
COPY setup.py /src/

ENV PATH="/.venv/bin:${PATH}"

RUN mkdir -p /.venv && \
    python -m venv /.venv \
    && pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements-stx.txt -c /tmp/constraints.txt \
    && pip install --no-cache-dir -e /src \
    && pip install --no-cache-dir --upgrade pip setuptools==78.1.1

FROM nexus3.onap.org:10001/onap/integration-python:12.0.0

ARG user=orano2
ARG group=orano2

USER root

# Upgrade packages to latest versions to mitigate CVEs
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    apk update \
    && apk add --upgrade expat busybox krb5 ncurses ncurses-dev sqlite sqlite-dev \
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

COPY helm_sdk/ /src/helm_sdk/

COPY configs/ /etc/o2/
COPY configs/ /configs/

COPY o2common/ /src/o2common/
COPY o2app/ /src/o2app/
COPY o2dms/ /src/o2dms/
COPY o2ims/ /src/o2ims/

WORKDIR /src

# USER $user
ENV PYTHONHASHSEED=0
ENV PATH="/.venv/bin:${PATH}"
