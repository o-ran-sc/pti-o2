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

from datetime import date, datetime
import sys
import pytest
from o2ims.adapter import ocloud_repository as repository
from o2ims.domain import ocloud
from o2ims import config
import logging
import uuid
import json
from o2ims.adapter.clients.ocloud_sa_client import StxSaOcloudClient
from o2ims.domain import stx_object as ocloudModel

# pytestmark = pytest.mark.usefixtures("mappers")


class FakeStxSaClientImp(object):
    def __init__(self):
        super().__init__()

    def getInstanceInfo(self) -> ocloudModel.StxGenericModel:
        model = ocloudModel.StxGenericModel()
        model.id = uuid.uuid4()
        model.name = "stx1"
        model.updatetime = datetime.now
        model.createtime = datetime.now
        model.content = json.dumps({})
        return model


@pytest.fixture
def fake_driver_imp():
    fakedriver = FakeStxSaClientImp()
    yield fakedriver


def test_get_instanceinfo(fake_driver_imp):
    logger = logging.getLogger(__name__)
    stxclientimp = StxSaOcloudClient(fake_driver_imp)
    assert stxclientimp is not None
    systeminfo = stxclientimp.get(None)
    assert systeminfo is not None
    assert systeminfo.id is not None
    assert systeminfo.name == "stx1"
    assert systeminfo.content == json.dumps({})
