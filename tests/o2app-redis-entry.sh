#!/bin/sh

# pip install -e /src
# python /o2ims/entrypoints/resource_watcher.py

# test only
if [ ! -e '/usr/local/bin/helm' ]; then
    apt-get install -y curl
    curl -O https://get.helm.sh/helm-v3.3.1-linux-amd64.tar.gz;
    tar -zxvf helm-v3.3.1-linux-amd64.tar.gz; cp linux-amd64/helm /usr/local/bin
fi

mkdir -p /etc/o2
cp -r /configs/* /etc/o2/
mkdir -p /src/o2common
cp -r /o2common/* /src/o2common
mkdir -p /src/o2ims
cp -r /o2ims/* /src/o2ims
mkdir -p /src/o2dms
cp -r /o2dms/* /src/o2dms
mkdir -p /src/o2app
cp -r /o2app/* /src/o2app
mkdir -p /src/helm_sdk
cp -r /helm_sdk/* /src/helm_sdk

pip install -e /src


python /o2app/entrypoints/redis_eventconsumer.py
