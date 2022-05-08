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

from multiprocessing.queues import Queue
import pytest
from o2app.entrypoints.resource_watcher import start_watchers
from multiprocessing import Process
from multiprocessing import Pipe
# pipe = Pipe()
# q = Queue()
import time
# pytestmark = pytest.mark.usefixtures("mappers")


def test_watcher_service():
    testedprocess = Process(target=start_watchers, args=())
    testedprocess.start()
    time.sleep(10)
    testedprocess.terminate()
