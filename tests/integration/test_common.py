# Copyright (C) 2021-2023 Wind River Systems, Inc.
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
import json
from urllib.parse import urlparse, urlunparse

from o2common.service.command.handler import SMOClient


def test_smo_with_oauth2():
    # Replace these with actual values
    client_id = 'client_id'
    token_url = 'http://128.224.115.32:1080/mock_smo/v1/auth/token'
    username = 'admin'
    password = 'admin'
    url = 'http://128.224.115.32:1080/mock_smo/v1/ocloud_observer'
    data = {"key": "value"}

    client = SMOClient(client_id=client_id, token_url=token_url,
                       username=username, password=password,
                       use_oauth=True)

    # Fetch the token
    client.fetch_token(client.session.verify)

    # Make a POST request
    response = client.post(url=url, data=json.dumps(data))

    # Check the status code
    assert response is True

    # Check the response data if you expect any
    # response_data = json.loads(response.text)
    # assert response_data == expected_data

    # --------------- HTTPS ---------------- #
    parsed_token_url = urlparse(token_url)
    parsed_token_url = parsed_token_url._replace(scheme='https')
    token_url1 = urlunparse(parsed_token_url)

    parsed_url = urlparse(url)
    parsed_url = parsed_url._replace(scheme='https')
    url1 = urlunparse(parsed_url)

    client = SMOClient(client_id=client_id, token_url=token_url1,
                       username=username, password=password,
                       use_oauth=True)

    # Fetch the token
    client.fetch_token(client.session.verify)

    # Make a POST request
    response = client.post(url=url1, data=json.dumps(data))

    # Check the status code
    assert response is True


def test_smo_client():
    url = 'http://128.224.115.32:1080/mock_smo/v1/o2ims_inventory_observer'
    data = {"key": "value"}

    client = SMOClient()

    # Make a POST request
    response = client.post(url=url, data=json.dumps(data))
    # Check the status code
    assert response is True

    # Check the response data if you expect any
    # response_data = json.loads(response.text)
    # assert response_data == expected_data

    parsed_url = urlparse(url)
    parsed_url = parsed_url._replace(scheme='https')
    url1 = urlunparse(parsed_url)

    # Make a POST request
    response = client.post(url=url1, data=json.dumps(data))
    # Check the status code
    assert response is True
