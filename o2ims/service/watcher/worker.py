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
import sched
from o2ims.service.watcher.base import BaseWatcher

import logging
logger = logging.getLogger(__name__)


class PollWorker(object):
    def __init__(self, interval=10) -> None:
        super().__init__()
        self.watchers = {}
        self.schedinstance = sched.scheduler(time.time, time.sleep)
        self.schedinterval = interval
        self._stopped = True

    def set_interval(self, interval):
        if interval > 0:
            self.schedinterval = interval
        else:
            raise Exception("Invalid interval:" + interval)

    def add_watcher(self, watcher: BaseWatcher):
        self.watchers[watcher.targetname()] = watcher

    def _repeat(self):
        logger.debug("_repeat started")
        if self._stopped:
            return
        for w in self.watchers.keys():
            try:
                logger.debug("about to probe:"+w)
                self.watchers[w].probe()
            except Exception as ex:
                logger.warning("Worker:" + w + " raises exception:" + str(ex))
                continue
        self.schedinstance.enter(self.schedinterval, 1, self._repeat)

    # note the sched run will block current thread
    def start(self):
        self._stopped = False
        logger.debug('about to start sched task')
        self.schedinstance.enter(self.schedinterval, 1, self._repeat)
        self.schedinstance.run()

    def stop(self):
        self._stopped = True
