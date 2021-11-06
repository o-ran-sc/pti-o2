#!/bin/sh

# pip install -e /src
# python /o2ims/entrypoints/resource_watcher.py

cp -r /o2ims/* /src/o2ims
pip install -e /src
python /o2ims/entrypoints/resource_watcher.py
