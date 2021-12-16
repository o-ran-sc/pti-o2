#!/bin/sh

mkdir -p /etc/o2
cp -r /configs/* /etc/o2/
mkdir -p /src/o2common
cp -r /o2common/* /src/o2common
mkdir -p /src/o2app
cp -r /o2app/* /src/o2app

pip install -e /src

export FLASK_APP=/o2app/entrypoints/mock_smo.py
flask run --host=0.0.0.0 --port=80
