#!/bin/sh

# pip install -e /src
# python /o2ims/entrypoints/resource_watcher.py

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

if [ -e '/tests/my-server-cert.pem' ]
then
cp /tests/my-root-ca-cert.pem /configs/my-root-ca-cert.pem
cp /tests/my-server-cert.pem /configs/server.crt
cp /tests/my-server-key.pem /configs/server.key
gunicorn -b [::]:80 o2app.entrypoints.flask_application:app --certfile /configs/server.crt  --keyfile /configs/server.key --log-level debug
else
gunicorn -b [::]:80 o2app.entrypoints.flask_application:app --log-level debug
fi
