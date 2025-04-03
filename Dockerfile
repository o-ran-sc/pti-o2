FROM nexus3.onap.org:10001/onap/integration-python:12.0.0 as build
# https://nexus3.onap.org/#browse/search=keyword%3Dintegration-python:d406d405e4cfbf1186265b01088caf9a
# https://git.onap.org/integration/docker/onap-python/tree/Dockerfile

USER root

# First install base packages from stable repository
RUN apk add --no-cache \
    git \
    curl \
    bluez-dev \
    bzip2-dev \
    dpkg-dev dpkg \
    gcc \
    libc-dev \
    libffi-dev \
    libnsl-dev \
    libtirpc-dev \
    linux-headers \
    make \
    openssl-dev \
    pax-utils \
    sqlite-dev \
    tcl-dev \
    tk \
    tk-dev \
    util-linux-dev \
    xz-dev \
    zlib-dev

# Then add edge main repository and install expat and fontconfig-dev
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    apk update && \
    apk add --no-cache --repository https://dl-cdn.alpinelinux.org/alpine/edge/main expat=2.7.0-r0 expat-dev=2.7.0-r0 fontconfig-dev && \
    curl -O https://get.helm.sh/helm-v3.3.1-linux-amd64.tar.gz && \
    tar -zxvf helm-v3.3.1-linux-amd64.tar.gz && \
    cp linux-amd64/helm /usr/local/bin && \
    rm -f helm-v3.3.1-linux-amd64.tar.gz

COPY requirements.txt /tmp/
COPY requirements-stx.txt /tmp/
COPY constraints.txt /tmp/
COPY setup.py /src/

ENV PATH="/.venv/bin:${PATH}"

RUN mkdir -p /.venv && \
    python -m venv /.venv \
    && pip install --no-cache-dir -r /tmp/requirements.txt -r /tmp/requirements-stx.txt -c /tmp/constraints.txt \
    && pip install --no-cache-dir -e /src

FROM nexus3.onap.org:10001/onap/integration-python:12.0.0

ARG user=orano2
ARG group=orano2

USER root

# First install base packages from stable repository
RUN apk add --no-cache bash curl

# Then add edge main repository and install dependencies
RUN echo "https://dl-cdn.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
    apk update && \
    # Install ncurses packages first from edge repository
    apk add --no-cache --repository https://dl-cdn.alpinelinux.org/alpine/edge/main \
        ncurses-dev \
        ncurses-terminfo-base \
        ncurses-libs && \
    # Install other build dependencies
    apk add --no-cache --repository https://dl-cdn.alpinelinux.org/alpine/edge/main \
        python3-dev \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
        bzip2-dev \
        zlib-dev \
        readline-dev \
        sqlite-dev \
        tcl-dev \
        tk-dev \
        make \
        linux-headers && \
    # Install expat
    apk add --no-cache --repository https://dl-cdn.alpinelinux.org/alpine/edge/main expat=2.7.0-r0 && \
    # Download and build Python from source
    cd /tmp && \
    curl -O https://www.python.org/ftp/python/3.12.2/Python-3.12.2.tgz && \
    tar xzf Python-3.12.2.tgz && \
    cd Python-3.12.2 && \
    ./configure --with-system-expat --without-readline && \
    make && \
    make install && \
    cd /tmp && \
    rm -rf Python-3.12.2 Python-3.12.2.tgz && \
    # Clean up build dependencies
    apk del --no-cache \
        python3-dev \
        gcc \
        musl-dev \
        libffi-dev \
        openssl-dev \
        bzip2-dev \
        zlib-dev \
        readline-dev \
        sqlite-dev \
        tcl-dev \
        tk-dev \
        make \
        linux-headers

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
