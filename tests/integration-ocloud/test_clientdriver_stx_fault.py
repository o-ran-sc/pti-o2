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

# import sys
# import logging
import pytest

from o2common.config import config
from o2ims.adapter.clients.fault_client import StxFaultClientImp
# from o2ims.adapter.clients.ocloud_client import StxClientImp
from cgtsclient.client import get_client as get_stx_client
from dcmanagerclient.api.client import client as get_dc_client
from fmclient.client import get_client as get_fm_client


@pytest.fixture
def real_stx_aio_client():
    os_client_args = config.get_stx_access_info()
    config_client = get_stx_client(**os_client_args)
    yield config_client


@pytest.fixture
def real_stx_dc_client():
    os_client_args = config.get_dc_access_info()
    config_client = get_dc_client(**os_client_args)
    yield config_client


@pytest.fixture
def real_stx_fm_client():
    os_client_args = config.get_fm_access_info()
    config_client = get_fm_client(1, **os_client_args)
    yield config_client

# pytestmark = pytest.mark.usefixtures("mappers")


def test_get_alarmlist(real_stx_fm_client):
    fmClientImp = StxFaultClientImp(real_stx_fm_client)
    assert fmClientImp is not None
    alarms = fmClientImp.getAlarmList()
    assert alarms is not None
    assert len(alarms) > 0


def test_get_alarminfo(real_stx_fm_client):
    fmClientImp = StxFaultClientImp(real_stx_fm_client)
    assert fmClientImp is not None
    alarms = fmClientImp.getAlarmList()
    assert alarms is not None
    assert len(alarms) > 0
    alarm1 = alarms[0]
    alarm2 = fmClientImp.getAlarmInfo(alarm1.id)
    assert alarm1 != alarm2
    assert alarm1.id == alarm2.id
    # fmClientImp.getAlarmInfo('f87478e9-4cec-44dc-8f13-9304445d4070')
    # assert fmClientImp is None


def test_get_eventlist(real_stx_fm_client):
    fmClientImp = StxFaultClientImp(real_stx_fm_client)
    assert fmClientImp is not None
    events = fmClientImp.getEventList()
    assert events is not None
    assert len(events) > 0


def test_get_eventinfo(real_stx_fm_client):
    fmClientImp = StxFaultClientImp(real_stx_fm_client)
    assert fmClientImp is not None
    events = fmClientImp.getEventList()
    assert events is not None
    assert len(events) > 0
    event1 = events[0]
    event2 = fmClientImp.getEventInfo(event1.id)
    assert event1 != event2
    assert event1.id == event2.id
