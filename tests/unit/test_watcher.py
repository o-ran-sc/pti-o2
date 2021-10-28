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

from datetime import datetime
import json
from typing import List
from o2ims.service.client.base_client import BaseClient
import pytest
from o2ims.domain import ocloud
from o2ims import config
import uuid
from o2ims.service.watcher.base import OcloudWather
from o2ims.domain import stx_object as ocloudModel
from o2ims.adapter.ocloud_repository import OcloudRepository

class FakeOcloudClient(BaseClient):
    def __init__(self):
        super().__init__()
        fakeCloud = ocloudModel.StxGenericModel()
        fakeCloud.id = uuid.uuid4()
        fakeCloud.name = 'stx1'
        fakeCloud.content = json.dumps({})
        fakeCloud.createtime = datetime.now()
        fakeCloud.updatetime = datetime.now
        self.fakeCloud = fakeCloud

    def _get(self, id) -> ocloudModel.StxGenericModel:
        return self.fakeCloud

    def _list(self):
        return [self.fakeCloud]

class FakeOcloudRepo(OcloudRepository):
    def __init__(self):
        super().__init__()
        self.oclouds = []

    def _add(self, ocloud: ocloud.Ocloud):
        self.oclouds.append(ocloud)

    def _get(self, ocloudid) -> ocloud.Ocloud:
        filtered = [o for o in self.oclouds if o.id == ocloudid]
        return filtered.pop()

    def _list(self) -> List[ocloud.Ocloud]:
        return [x for x in self.oclouds]

    def _update(self, ocloud: ocloud.Ocloud):
        filtered = [o for o in self.oclouds if o.id == ocloud.id]
        assert len(filtered) == 1
        ocloud1 = filtered.pop()
        ocloud1.update_by(ocloud)

def test_probe_new_ocloud():
    fakeRepo = FakeOcloudRepo()
    fakeClient = FakeOcloudClient()
    ocloudwatcher = OcloudWather(fakeClient, fakeRepo)
    ocloudwatcher.probe()
    assert len(fakeRepo.oclouds) == 1
    assert fakeRepo.oclouds[0].name == "stx1"
