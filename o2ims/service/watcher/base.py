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

from o2ims.service.client.base_client import BaseClient
from o2ims.domain.stx_object import StxGenericModel
from o2ims.service.unit_of_work import AbstractUnitOfWork

from o2common.helper import logger
logger = logger.get_logger(__name__)


class BaseWatcher(object):
    def __init__(self, client: BaseClient,
                 uow: AbstractUnitOfWork) -> None:
        super().__init__()
        self._client = client
        self._uow = uow

    def targetname(self) -> str:
        return self._targetname()

    def probe(self, parent: object = None):
        return self._probe(parent)

    def _probe(self, parent: object = None):
        raise NotImplementedError

    def _targetname(self):
        raise NotImplementedError

    def _compare_and_update(self, newmodel: StxGenericModel) -> bool:
        with self._uow:
            # localmodel = self._uow.stxobjects.get(ocloudmodel.id)
            localmodel = self._uow.stxobjects.get(str(newmodel.id))
            if not localmodel:
                logger.info("add entry:" + newmodel.name)
                self._uow.stxobjects.add(newmodel)
            elif localmodel.is_outdated(newmodel):
                logger.info("update entry:" + newmodel.name)
                localmodel.update_by(newmodel)
                self._uow.stxobjects.update(localmodel)
            self._uow.commit()


# node to organize watchers in tree hierachy
class WatcherTree(object):
    def __init__(self, watcher: BaseWatcher) -> None:
        super().__init__()
        self.watcher = watcher
        self.children = {}

    def addchild(self, watcher: BaseWatcher) -> object:
        child = WatcherTree(watcher)
        self.children[watcher.targetname()] = child
        return child

    def removechild(self, targetname: str) -> object:
        return self.children.pop(targetname)

    # probe all resources by parent, depth = 0 for indefinite recursive
    def probe(self, parentresource=None, depth: int = 0):
        logger.debug("probe resources with watcher: "
                     + self.watcher.targetname())
        childdepth = depth - 1 if depth > 0 else 0
        resources = self.watcher.probe(parentresource)
        logger.debug("probe returns " + str(len(resources)) + "resources")

        if depth == 1:
            # stop recursive
            return

        for res in resources:
            for targetname in self.children.keys():
                self.children[targetname].probe(res, childdepth)
