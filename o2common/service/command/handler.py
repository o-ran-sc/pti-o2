# Copyright (C) 2022 Wind River Systems, Inc.
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

import http.client
import ssl
from o2common.helper import o2logging

logger = o2logging.get_logger(__name__)


def post_data(conn, path, data):
    headers = {'Content-type': 'application/json'}
    conn.request('POST', path, data, headers)
    resp = conn.getresponse()
    data = resp.read().decode('utf-8')
    # json_data = json.loads(data)
    if resp.status >= 200 and resp.status <= 299:
        logger.info('Post data to SMO successed, response code {} {}, data {}'.
                    format(resp.status, resp.reason, data))
        return True, resp.status
    logger.error('Response code is: {}'.format(resp.status))
    return False, resp.status


def get_http_conn(callbackurl):
    conn = http.client.HTTPConnection(callbackurl)
    return conn


# with default CA
def get_https_conn_default(callbackurl):
    sslctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    sslctx.check_hostname = True
    sslctx.verify_mode = ssl.CERT_REQUIRED
    sslctx.load_default_certs()
    conn = http.client.HTTPSConnection(callbackurl, context=sslctx)
    return conn


# with self signed ca
def get_https_conn_selfsigned(callbackurl):
    sslctx = ssl.create_default_context(
        purpose=ssl.Purpose.SERVER_AUTH)
    smo_ca_path = config.get_smo_ca_config_path()
    sslctx.load_verify_locations(smo_ca_path)
    sslctx.check_hostname = False
    sslctx.verify_mode = ssl.CERT_REQUIRED
    conn = http.client.HTTPSConnection(callbackurl, context=sslctx)
    return conn
