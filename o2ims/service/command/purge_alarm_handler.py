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

from fmclient.common.exceptions import HTTPNotFound
from o2common.adapter.notifications import AbstractNotifications
from o2common.helper import o2logging
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.adapter.clients.fault_client import StxAlarmClient
from o2ims.domain import commands, alarm_obj
logger = o2logging.get_logger(__name__)


def purge_alarm_event(
    cmd: commands.PubAlarm2SMO,
    uow: AbstractUnitOfWork,
    notifications: AbstractNotifications,
):
    """
    Purge an alarm event.

    This method performs the following steps:
    1. Retrieves data from the command object and initializes the fault client.
    2. Uses the Unit of Work pattern to find and delete the corresponding
       alarm event record.
    3. Commits the changes to the database.

    Parameters:
    - cmd (commands.PubAlarm2SMO): Command object containing the alarm
      event data.
    - uow (AbstractUnitOfWork): Unit of Work object for managing
      database transactions.
    - notifications (AbstractNotifications): Abstract notifications
      object for sending notifications.

    Exceptions:
    - Any exceptions that might occur during database operations or
      notification sending.
    """
    fault_client = StxAlarmClient(uow)
    data = cmd.data
    with uow:
        alarm_event_record = uow.alarm_event_records.get(data.id)
        if str(alarm_event_record.perceivedSeverity) != \
                alarm_obj.PerceivedSeverityEnum.CLEARED.value:
            try:
                fault_client.delete(alarm_event_record.alarmEventRecordId)
            except HTTPNotFound:
                logger.info(
                    f'Alarm {alarm_event_record.alarmEventRecordId} '
                    'already deleted from fault management system'
                )
            except Exception as e:
                logger.warning(
                    f'Failed to delete alarm '
                    f'{alarm_event_record.alarmEventRecordId} '
                    f'from fault management system: {str(e)}. '
                    'Continuing with database purge.'
                )

        uow.alarm_event_records.delete(alarm_event_record)
        uow.commit()
        logger.debug(f'Successfully purge alarm event record: {data.id}')
