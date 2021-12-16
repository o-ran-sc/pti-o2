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

import os

import mock_smo.logging as logging
logger = logging.get_logger(__name__)


def get_mock_smo_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 5001 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_root_api_base():
    return "/"


def get_o2ims_api_base():
    return get_root_api_base() + 'o2ims_infrastructureInventory/v1'


def get_o2dms_api_base():
    return get_root_api_base() + "o2dms"


def get_redis_host_and_port():
    host = os.environ.get("REDIS_HOST", "localhost")
    port = 63792 if host == "localhost" else 6379
    return dict(host=host, port=port)


def get_smo_o2endpoint():
    smo_o2endpoint = os.environ.get(
        "SMO_O2_ENDPOINT", "http://localhost/smo_sim")
    return smo_o2endpoint
