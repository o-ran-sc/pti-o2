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


def test_get_pserverlist(real_stx_aio_client):
    stxSaClientImp = StxSaClientImp(real_stx_aio_client)
    assert stxSaClientImp is not None
    hosts = stxSaClientImp.getPserverList()
    assert hosts is not None
    assert len(hosts) > 0


def test_get_pserver(real_stx_aio_client):
    stxSaClientImp = StxSaClientImp(real_stx_aio_client)
    assert stxSaClientImp is not None
    hosts = stxSaClientImp.getPserverList()
    assert hosts is not None
    assert len(hosts) > 0
    host1 = hosts[0]
    host2 = stxSaClientImp.getPserver(host1.id)
    assert host1 != host2
    assert host1.id == host2.id

def test_get_k8s_list(real_stx_aio_client):
    stxSaClientImp = StxSaClientImp(real_stx_aio_client)
    assert stxSaClientImp is not None
    k8slist = stxSaClientImp.getK8sList()
    assert k8slist is not None
    assert len(k8slist) > 0
    k8s1 = k8slist[0]
    k8s2 = stxSaClientImp.getK8sDetail(k8s1.name)
    assert k8s1 != k8s2
    assert k8s1.name == k8s2.name
    assert k8s1.id == k8s2.id

def test_get_cpu_list(real_stx_aio_client):
    stxSaClientImp = StxSaClientImp(real_stx_aio_client)
    assert stxSaClientImp is not None
    hostlist = stxSaClientImp.getPserverList()
    assert len(hostlist) > 0

    cpulist = stxSaClientImp.getCpuList(hostlist[0].id)
    assert len(cpulist) > 0
    cpu1 = cpulist[0]
    cpu2 = stxSaClientImp.getCpu(cpu1.id)
    assert cpu1 != cpu2
    assert cpu1.id == cpu2.id
