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

# from logging import exception
# from cgtsclient import exc
from o2common.service.client.base_client import BaseClient
from o2common.domain import commands
from o2common.service.messagebus import MessageBus
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class BaseWatcher(object):
    def __init__(self, client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__()
        self._client = client
        self._bus = bus
        # self._uow = bus.uow

    def targetname(self) -> str:
        return self._targetname()

    def probe(self, parent: commands.Command = None):
        try:
            cmds = self._probe(parent.data if parent else None)
            for cmd in cmds:
                self._bus.handle(cmd)

            # return self._probe(parent)
            return cmds
        except Exception as ex:
            logger.warning("Failed to probe resource due to: " + str(ex))
            return []

    def _probe(self, parent: object = None) -> commands.Command:
        raise NotImplementedError

    def _targetname(self):
        raise NotImplementedError

    # def _compare_and_update(self, newmodel: StxGenericModel) -> bool:
    #     with self._uow:
    #         # localmodel = self._uow.stxobjects.get(ocloudmodel.id)
    #         localmodel = self._uow.stxobjects.get(str(newmodel.id))
    #         if not localmodel:
    #             logger.info("add entry:" + newmodel.name)
    #             self._uow.stxobjects.add(newmodel)
    #         elif localmodel.is_outdated(newmodel):
    #             logger.info("update entry:" + newmodel.name)
    #             localmodel.update_by(newmodel)
    #             self._uow.stxobjects.update(localmodel)
    #         self._uow.commit()


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
        logger.debug("probe returns " + str(len(resources)) + " resources")

        if depth == 1:
            # stop recursive
            return

        for res in resources:
            for targetname in self.children.keys():
                self.children[targetname].probe(res, childdepth)
