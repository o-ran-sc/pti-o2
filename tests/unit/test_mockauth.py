# Copyright (C) 2021 Wind River Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from concurrent.futures import thread
from unittest.mock import MagicMock
from flask import Flask, request
from o2common.authmw import authmiddleware
import _thread
# server.py
import http.server
import socketserver


def test_setup_sampleapp():

    app = Flask('DemoApp')

    # call middleware
    app.wsgi_app = authmiddleware.authmiddleware(app.wsgi_app)

    @app.route('/authenticate', methods=['GET', 'POST'])
    def hello():
        return "Hi"

    return app
    """     try:
        thread.start_new_thread(hello, ())
    except:
        print("Error: unable to start thread")
        app.run('127.0.0.1', '5000', debug=True) """


def test_setup_simple_http_server():
    addr = 'localhost'
    port = '8008'
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((addr, port), handler)
    print("HTTP server is at: http://%s:%d/" % (addr, port))
    return httpd


def test_startup_mock_k8s_apiserver():
    pass
