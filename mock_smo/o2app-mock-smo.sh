#!/bin/sh

mkdir -p /etc/mock_smo
cp -r /tmp/etc/* /etc/mock_smo/
mkdir -p /src/mock_smo
cp -r /mock_smo/* /src/mock_smo

# cp -r requirements.txt /src/requirements.txt

pip install -e /src

export FLASK_APP=/mock_smo/entrypoints/mock_smo.py
flask run --host=0.0.0.0 --port=80
