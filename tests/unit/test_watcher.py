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

import time
from datetime import datetime
import json
from typing import List
from o2ims.domain.resource_type import ResourceTypeEnum
from o2ims.service.client.base_client import BaseClient
from o2ims.domain import ocloud
from o2ims import config
import uuid
from o2ims.service.watcher.base import BaseWatcher, OcloudWatcher
from o2ims.domain import stx_object as ocloudModel
from o2ims.adapter.ocloud_repository import OcloudRepository
from o2ims.domain.stx_repo import StxObjectRepository
from o2ims.service.watcher import worker
from o2ims.service.unit_of_work import AbstractUnitOfWork


class FakeOcloudClient(BaseClient):
    def __init__(self):
        super().__init__()
        fakeCloud = ocloudModel.StxGenericModel(ResourceTypeEnum.OCLOUD)
        fakeCloud.id = uuid.uuid4()
        fakeCloud.name = 'stx1'
        fakeCloud.content = json.dumps({})
        fakeCloud.createtime = datetime.now()
        fakeCloud.updatetime = datetime.now()
        fakeCloud.hash = str(hash((fakeCloud.id, fakeCloud.updatetime)))
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



class FakeStxObjRepo(StxObjectRepository):
    def __init__(self):
        super().__init__()
        self.oclouds = []

    def _add(self, ocloud: ocloud.Ocloud):
        self.oclouds.append(ocloud)

    def _get(self, ocloudid) -> ocloud.Ocloud:
        filtered = [o for o in self.oclouds if o.id == ocloudid]
        return filtered.pop()

    def _list(self, type: ResourceTypeEnum) -> List[ocloud.Ocloud]:
        return [x for x in self.oclouds]

    def _update(self, ocloud: ocloud.Ocloud):
        filtered = [o for o in self.oclouds if o.id == ocloud.id]
        assert len(filtered) == 1
        ocloud1 = filtered.pop()
        ocloud1.update_by(ocloud)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        pass

    def __enter__(self):
        # self.session = self.session_factory()  # type: Session
        # self.oclouds = OcloudSqlAlchemyRepository(self.session)
        self.stxobjects = FakeStxObjRepo()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        # self.session.close()

    def _commit(self):
        pass
        # self.session.commit()

    def rollback(self):
        pass
        # self.session.rollback()


def test_probe_new_ocloud():
    # fakeRepo = FakeOcloudRepo()
    fakeuow = FakeUnitOfWork()
    fakeClient = FakeOcloudClient()
    ocloudwatcher = OcloudWatcher(fakeClient, fakeuow)
    ocloudwatcher.probe()
    assert len(fakeuow.stxobjects.oclouds) == 1
    assert fakeuow.stxobjects.oclouds[0].name == "stx1"


def test_watchers_worker():
    testedworker = worker.PollWorker()

    class FakeOCloudWatcher(BaseWatcher):
        def __init__(self, client: BaseClient,
                     repo: OcloudRepository) -> None:
            super().__init__(client)
            self.fakeOcloudWatcherCounter = 0
            self._client = client
            self._repo = repo

        def _targetname(self):
            return "fakeocloudwatcher"

        def _probe(self):
            self.fakeOcloudWatcherCounter += 1
            # hacking to stop the blocking sched task
            if self.fakeOcloudWatcherCounter > 2:
                testedworker.stop()


    # fakeRepo = FakeOcloudRepo()
    fakeuow = FakeUnitOfWork()

    fakeClient = FakeOcloudClient()
    fakewatcher = FakeOCloudWatcher(fakeClient, fakeuow)

    testedworker.set_interval(1)
    testedworker.add_watcher(fakewatcher)
    assert fakewatcher.fakeOcloudWatcherCounter == 0

    count1 = fakewatcher.fakeOcloudWatcherCounter
    testedworker.start()
    time.sleep(20)
    assert fakewatcher.fakeOcloudWatcherCounter > count1

    # assumed hacking: probe has stopped the sched task
    count3 = fakewatcher.fakeOcloudWatcherCounter
    time.sleep(3)
    assert fakewatcher.fakeOcloudWatcherCounter == count3
