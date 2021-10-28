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

import sys
import pytest
from o2ims.adapter import ocloud_repository as repository
from o2ims.domain import ocloud
from o2ims import config
import uuid
from o2ims.adapter.clients.ocloud_sa_client import StxSaClientImp
from cgtsclient.client import get_client

import logging


@pytest.fixture
def real_stx_aio_client():
    os_client_args = config.get_stx_access_info()
    # os_client_args['os_auth_url'] = 'http://128.224.115.15:5000/v3'
    # os_client_args['os_password'] = 'Li69nux*'
    # os_client_args['os_project_name'] = 'admin'
    config_client = get_client(**os_client_args)
    yield config_client

# pytestmark = pytest.mark.usefixtures("mappers")


def test_get_instanceinfo(real_stx_aio_client):
    logger = logging.getLogger(__name__)
    stxclientimp = StxSaClientImp(real_stx_aio_client)
    assert stxclientimp is not None
    systeminfo = stxclientimp.getInstanceInfo()
    assert systeminfo is not None
    assert systeminfo.id is not None
    assert systeminfo.name is not None
    assert systeminfo.content is not None

