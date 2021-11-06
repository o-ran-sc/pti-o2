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

import cotyledon

from o2ims.service.watcher.worker import PollWorker
from o2ims.service.watcher.base import OcloudWatcher
from o2ims.service.watcher.base import DmsWatcher
# from o2ims.service.client.base_client import BaseClient
from o2ims.adapter.clients.ocloud_sa_client import StxSaDmsClient
from o2ims.adapter.clients.ocloud_sa_client import StxSaOcloudClient

from o2ims import bootstrap
# from o2ims import config
# import redis

import logging
logger = logging.getLogger(__name__)

# r = redis.Redis(**config.get_redis_host_and_port())


class WatcherService(cotyledon.Service):
    def __init__(self, worker_id, args=None) -> None:
        super().__init__(worker_id)
        self.args = args
        self.bus = bootstrap.bootstrap()
        self.worker = PollWorker()
        # self.stxrepo = self.bus.uow.stxobjects
        # tbd: 1 client per resource pool
        # self.client = StxSaOcloudClient()

    def run(self):
        try:
            self.worker.add_watcher(OcloudWatcher(StxSaOcloudClient(),
                                    self.bus.uow))
            self.worker.add_watcher(DmsWatcher(StxSaDmsClient(),
                                    self.bus.uow))
            self.worker.start()
        except Exception as ex:
            logger.warning("WorkerService Exception:" + str(ex))
        finally:
            self.worker.stop()


def start_watchers(sm: cotyledon.ServiceManager = None):
    watchersm = sm if sm else cotyledon.ServiceManager()
    watchersm.add(WatcherService, workers=1, args=())
    watchersm.run()


def main():
    logger.info("Resource watcher starting")
    start_watchers()


if __name__ == "__main__":
    main()
