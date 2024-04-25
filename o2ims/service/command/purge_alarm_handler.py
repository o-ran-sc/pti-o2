# Copyright (C) 2024 Wind River Systems, Inc.
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

import json

from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.adapter.notifications import AbstractNotifications

from o2ims.adapter.clients.fault_client import StxEventClient
from o2ims.domain import commands, alarm_obj

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def purge_alarm_event(
    cmd: commands.PubAlarm2SMO,
    uow: AbstractUnitOfWork,
    notifications: AbstractNotifications,
):
    logger.debug('In purge_alarm_event')
    fault_client = StxEventClient(uow)
    data = cmd.data
    with uow:
        alarm_event_record = uow.alarm_event_records.get(data.id)
        alarm_id = json.loads(alarm_event_record.extensions).get('alarm_id')

        events = fault_client.suppression_list(alarm_id)
        for event_id in events:
            event = fault_client.suppress(event_id.id)
            alarm_event_record.hash = event.hash
            alarm_event_record.extensions = json.dumps(event.filtered)
            alarm_event_record.alarmChangedTime = event.updatetime.\
                strftime("%Y-%m-%dT%H:%M:%S")
            alarm_event_record.perceivedSeverity = \
                alarm_obj.PerceivedSeverityEnum.CLEARED

            uow.alarm_event_records.update(alarm_event_record)
            break
        uow.commit()
