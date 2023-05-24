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

import os
import requests
import http.client
import ssl
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, SSLError

from o2common.helper import o2logging
from o2common.config import config

logger = o2logging.get_logger(__name__)


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


class SMOClient:
    def __init__(self, client_id=None, token_url=None, username=None,
                 password=None, scope=None, retries=3, use_oauth=False):
        self.client_id = client_id
        self.token_url = token_url
        self.username = username
        self.password = password
        self.scope = scope if scope else []
        self.use_oauth = use_oauth
        self.retries = retries

        if self.use_oauth:
            if not all([self.client_id, self.token_url, self.username,
                        self.password]):
                raise ValueError(
                    'client_id, token_url, username, and password ' +
                    'must be provided when use_oauth is True.')

            # Set OAUTHLIB_INSECURE_TRANSPORT environment variable
            # if token_url uses http
            if 'http://' in self.token_url:
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

            # Create a LegacyApplicationClient for handling password flow
            client = LegacyApplicationClient(client_id=self.client_id)
            self.session = OAuth2Session(client=client)

            # Check if token_url uses https and set SSL verification
            if 'https://' in self.token_url:
                ca_path = config.get_smo_ca_config_path()
                if os.path.exists(ca_path):
                    self.session.verify = ca_path
                else:
                    self.session.verify = True

            # Fetch the access token
            self.fetch_token(self.session.verify)
        else:
            self.session = requests.Session()

        # Create a Retry object for handling retries
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def fetch_token(self, verify):
        try:
            self.session.fetch_token(
                token_url=self.token_url,
                username=self.username,
                password=self.password,
                client_id=self.client_id,
                verify=verify
            )
        except SSLError:
            # If SSLError is raised, try again with verify=False
            logger.warning('The SSLError occurred')
            if verify is not False:
                self.fetch_token(verify=False)

    def handle_post_data(self, resp):
        if resp.status_code >= 200 and resp.status_code < 300:
            return True
        logger.error('Response code is: {}'.format(resp.status_code))
        # TODO: write the status to extension db table.
        return False

    def post(self, url, data, retries=1):
        if not all([url, data]):
            raise ValueError(
                'url, data must be provided when call the post.')

        # Check if token_url uses https and set SSL verification
        if 'https://' in url:
            ca_path = config.get_smo_ca_config_path()
            if os.path.exists(ca_path):
                self.session.verify = ca_path
            else:
                self.session.verify = True

        if retries is None:
            retries = self.retries

        for _ in range(retries):
            try:
                response = self.session.post(url, json=data)
                response.raise_for_status()
                return self.handle_post_data(response)
            except (SSLError, RequestException) as e:
                logger.warning(f'Error occurred: {e}')
                pass
        raise Exception(
            f"POST request to {url} failed after {retries} retries.")
