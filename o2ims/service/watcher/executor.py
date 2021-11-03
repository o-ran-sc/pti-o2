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

from o2ims.service.watcher.base import BaseWatcher
from o2ims.service.watcher.base import OcloudWather
from o2ims.service.watcher.base import DmsWatcher

import logging
logger = logging.getLogger(__name__)


class WatcherService(cotyledon.Service):
    def __init__(self, worker_id, args) -> None:
        super().__init__(worker_id)
        self.args = args
        self.worker = PollWorker()
    
    def run(self):
        try:
            self.worker.add_watcher(OcloudWather())
            self.worker.add_watcher(DmsWatcher())
            self.worker.start()
        except Exception as ex:
            logger.warning(ex.message)
        finally:
            self.worker.stop()


def start_watchers(sm = None):
    watchersm = sm if sm else cotyledon.ServiceManager()
    watchersm.add(WatcherService, workers = 1, args=())
    return watchersm
