#!/bin/sh

# pip install -e /src
# python /o2ims/entrypoints/resource_watcher.py

cp -r /configs/* /etc/o2/
cp -r /o2common/* /src/o2common
cp -r /o2ims/* /src/o2ims
cp -r /o2dms/* /src/o2dms
pip install -e /src
python /o2ims/entrypoints/redis_eventconsumer.py
