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

# from o2ims.domain.resource_type import ResourceTypeEnum
from o2common.service.client.base_client import BaseClient
# from o2ims.domain.stx_object import StxGenericModel
# from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.service.watcher.base import BaseWatcher
from o2common.service.messagebus import MessageBus
from o2ims.domain import commands

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class AlarmWatcher(BaseWatcher):
    def __init__(self, fault_client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__(fault_client, bus)

    def _targetname(self):
        return "alarm"

    def _probe(self, parent: object = None, tags: object = None):
        newmodels = self._client.list()
        # if len(newmodels) == 0:
        #     return []

        # uow = self._bus.uow
        # exist_alarms = {}
        # with uow:
        #     rs = uow.session.execute(
        #         '''
        #         SELECT "alarmEventRecordId"
        #         FROM "alarmEventRecord"
        #         WHERE "perceivedSeverity" != :perceived_severity_enum
        #         ''',
        #         dict(perceived_severity_enum=alarm_obj.PerceivedSeverityEnum.
        #              CLEARED)
        #     )
        #     for row in rs:
        #         id = row[0]
        #         # logger.debug('Exist alarm: ' + id)
        #         exist_alarms[id] = False

        # ret = []
        # for m in newmodels:
        #     try:
        #         if exist_alarms[m.id]:
        #             ret.append(commands.UpdateAlarm(m))
        #             exist_alarms[m.id] = True
        #     except KeyError:
        #         logger.debug('alarm new: ' + m.id)
        #         ret.append(commands.UpdateAlarm(m))

        # for alarm in exist_alarms:
        #     logger.debug('exist alarm: ' + alarm)
        #     if exist_alarms[alarm]:
        #         # exist alarm is active
        #         continue
        #     event = self._client.get(alarm)
        #     ret.append(commands.UpdateAlarm(event))

        # return ret

        return [commands.UpdateAlarm(m) for m in newmodels] \
            if len(newmodels) > 0 else []


# class EventWatcher(BaseWatcher):
#     def __init__(self, fault_client: BaseClient,
#                  bus: MessageBus) -> None:
#         super().__init__(fault_client, bus)

#     def _targetname(self):
#         return "event"

#     def _probe(self, parent: object = None, tags: object = None):
#         newmodels = self._client.list()
#         return [commands.UpdateAlarm(m) for m in newmodels] \
#             if len(newmodels) > 0 else []
