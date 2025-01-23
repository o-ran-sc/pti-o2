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

from o2app import bootstrap
from o2common.service.watcher.base import WatcherTree
from o2common.service.watcher.worker import PollWorker

from o2ims.service.watcher.ocloud_watcher import OcloudWatcher
from o2ims.service.watcher.ocloud_watcher import DmsWatcher
from o2ims.service.watcher.resourcepool_watcher import ResourcePoolWatcher
from o2ims.service.watcher.alarm_watcher import AlarmWatcher

from o2ims.adapter.clients.ocloud_client import StxDmsClient
from o2ims.adapter.clients.ocloud_client import StxOcloudClient
from o2ims.adapter.clients.ocloud_client import StxResourcePoolClient
from o2ims.adapter.clients.fault_client import StxAlarmClient

from o2ims.service.watcher.pserver_watcher import PServerWatcher
from o2ims.adapter.clients.ocloud_client import StxPserverClient

from o2ims.service.watcher.pserver_cpu_watcher import PServerCpuWatcher
from o2ims.adapter.clients.ocloud_client import StxCpuClient

from o2ims.service.watcher.pserver_mem_watcher import PServerMemWatcher
from o2ims.adapter.clients.ocloud_client import StxMemClient

from o2ims.service.watcher.pserver_if_watcher import PServerIfWatcher
from o2ims.adapter.clients.ocloud_client import StxIfClient

# from o2ims.service.watcher.pserver_port_watcher import PServerIfPortWatcher
# from o2ims.adapter.clients.ocloud_client import StxIfPortClient

from o2ims.service.watcher.pserver_eth_watcher import PServerEthWatcher
from o2ims.adapter.clients.ocloud_client import StxEthClient

# from o2ims.service.watcher.pserver_dev_watcher import PServerDevWatcher
# from o2ims.adapter.clients.ocloud_client import StxDevClient
from o2ims.service.watcher.pserver_acc_watcher import PServerAccWatcher
from o2ims.adapter.clients.ocloud_client import StxAccClient

from o2ims.adapter.clients.alarm_dict_client import load_alarm_definition,\
    load_alarm_dictionary_from_conf_file
from o2ims.service.watcher.agg_compute_watcher import ComputeAggWatcher
from o2ims.service.watcher.agg_network_watcher import NetworkAggWatcher
from o2ims.service.watcher.agg_storage_watcher import StorageAggWatcher
from o2ims.service.watcher.agg_undefined_watcher import UndefinedAggWatcher
from o2ims.adapter.clients.aggregate_client import ComputeAggClient, \
    NetworkAggClient, StorageAggClient, UndefinedAggClient

from o2ims.adapter.clients.pm_client import MeasurementJobClient
from o2ims.service.watcher.measurement_watcher import MeasurementWatcher

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)

# r = redis.Redis(**config.get_redis_host_and_port())


class WatcherService(cotyledon.Service):
    def __init__(self, worker_id, args=None) -> None:
        super().__init__(worker_id)
        self.args = args
        self.bus = bootstrap.bootstrap()
        self.worker = PollWorker(bus=self.bus)
        load_alarm_definition(self.bus.uow)
        load_alarm_dictionary_from_conf_file(self.bus.uow)

    def run(self):
        try:
            root = WatcherTree(OcloudWatcher(
                StxOcloudClient(), self.bus))
            root.addchild(
               DmsWatcher(StxDmsClient(), self.bus))

            child_respool = root.addchild(
                ResourcePoolWatcher(StxResourcePoolClient(),
                                    self.bus))

            # Add Aggregate watch
            child_respool.addchild(
                ComputeAggWatcher(ComputeAggClient(), self.bus))
            child_respool.addchild(
                NetworkAggWatcher(NetworkAggClient(), self.bus))
            child_respool.addchild(
                StorageAggWatcher(StorageAggClient(), self.bus))
            child_respool.addchild(
                UndefinedAggWatcher(UndefinedAggClient(), self.bus))

            # Add Resource watch
            child_pserver = child_respool.addchild(
                PServerWatcher(StxPserverClient(), self.bus))
            child_pserver.addchild(
                PServerCpuWatcher(StxCpuClient(), self.bus))
            child_pserver.addchild(
                PServerMemWatcher(StxMemClient(), self.bus))
            child_pserver.addchild(
                PServerEthWatcher(StxEthClient(), self.bus))
            child_pserver.addchild(
                PServerIfWatcher(StxIfClient(), self.bus))
            # child_if.addchild(
            #     PServerIfPortWatcher(StxIfPortClient(), self.bus))
            # child_pserver.addchild(
            #     PServerDevWatcher(StxDevClient(), self.bus))
            child_pserver.addchild(
                PServerAccWatcher(StxAccClient(), self.bus))

            # Add Alarm watch
            child_respool.addchild(
                AlarmWatcher(StxAlarmClient(self.bus.uow), self.bus))

            # Add Measurement watch
            child_respool.addchild(
                MeasurementWatcher(MeasurementJobClient(self.bus.uow),
                                   self.bus))

            self.worker.add_watcher(root)

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
