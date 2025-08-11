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

from o2common.domain import tags
from o2common.service.messagebus import MessageBus
from o2common.service.watcher.base import BaseWatcher
from o2common.service.client.base_client import BaseClient

from o2ims.domain import commands
from o2ims.domain.stx_object import StxGenericModel
from o2ims.domain.alarm_obj import PerceivedSeverityEnum, \
    AlarmNotificationEventEnum
from o2ims.domain import events

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class AlarmWatcher(BaseWatcher):
    def __init__(self, fault_client: BaseClient,
                 bus: MessageBus) -> None:
        super().__init__(fault_client, bus)
        self._tags = tags.Tag()
        self.poolid = None

    def _targetname(self):
        return "alarm"

    def _prune_stale_alarms(self):
        """Prune DB alarms that don't exist in FM for the current respool.

        Steps:
        - Get FM alarm IDs for the configured resource pool(subcloud)
        - Get DB alarm IDs for alarms whose resources belong to this res pool
        - Find stale DB alarms that are not present in the source(fm alarms)
          and delete them
        """
        pool_id = getattr(self._client, '_pool_id', None)
        if not pool_id:
            return

        # FM alarm IDs for this pool with one quick retry on empty
        fm_list = self._client.list()

        fm_ids = {a.id for a in fm_list}

        # DB alarm IDs for this pool via join
        with self._bus.uow as uow:
            rs = uow.session.execute(
                '''
                SELECT a."alarmEventRecordId"
                FROM "alarmEventRecord" a
                JOIN "resource" r ON a."resourceId" = r."resourceId"
                WHERE r."resourcePoolId" = :pool_id
                ''',
                dict(pool_id=pool_id)
            )

            db_ids = {row[0] for row in rs}
            if not db_ids:
                return  # No results, exit early

            # Delete stale DB alarms that are not present in the source
            to_delete = db_ids - fm_ids

            # No pruning of alarms required
            if not to_delete:
                return

            # TODO: When an alarm is deleted, the SMO must be notified.
            for alarm_id in to_delete:
                obj = uow.alarm_event_records.get(alarm_id)
                if obj:
                    uow.alarm_event_records.delete(obj)
                    logger.info(f'Pruning alarm: {alarm_id}')
            uow.commit()

    def _probe(self, parent: StxGenericModel, tags: object = None):

        # Set a tag for children resource
        self._tags.pool = parent.res_pool_id
        self._set_respool_client()

        resourcepoolid = parent.id

        # Check and clear the pruned alarms
        self._prune_stale_alarms()
        # Check and delete expired alarms before getting new alarms
        self._check_and_delete_expired_alarms()

        newmodels = self._client.list()
        return [commands.UpdateAlarm(m, resourcepoolid) for m in newmodels] \
            if len(newmodels) > 0 else []

    def _set_respool_client(self):
        self.poolid = self._tags.pool
        self._client.set_pool_driver(self.poolid)

    def _check_and_delete_expired_alarms(self):
        """Check and delete expired alarms based on retention period.
        Only delete alarms that are either cleared or acknowledged."""
        try:
            with self._bus.uow as uow:
                # Get retention period from alarm service configuration
                # This will create default config if not exists
                alarm_config = uow.alarm_service_config.get()
                # Convert retention period from days to seconds
                retention_period = alarm_config.retentionPeriod * 24 * 3600

                # Query expired alarms that are either cleared or acknowledged
                rs = uow.session.execute(
                    '''
                    SELECT "alarmEventRecordId"
                    FROM "alarmEventRecord"
                    WHERE ("perceivedSeverity" = :perceived_severity_enum
                    OR "alarmAcknowledged" = 'true')
                    AND (EXTRACT(EPOCH FROM NOW()) -
                         EXTRACT(EPOCH FROM TO_TIMESTAMP(
                            "alarmRaisedTime", 'YYYY-MM-DD"T"HH24:MI:SS')))
                        > :retention_period
                    ''',
                    dict(
                        retention_period=retention_period,
                        perceived_severity_enum=PerceivedSeverityEnum.CLEARED
                    )
                )

                # Process expired alarms
                for row in rs:
                    alarm_id = row[0]
                    try:
                        logger.debug(
                            f'Processing expired alarm for deletion: '
                            f'{alarm_id}')

                        # Add purge event before deletion
                        alarm_event = events.AlarmEventPurged(
                            id=alarm_id,
                            notificationEventType=(
                                AlarmNotificationEventEnum.CLEAR)
                        )

                        # Update alarm event record with purge event
                        alarm_record = uow.alarm_event_records.get(alarm_id)
                        if alarm_record:
                            alarm_record.events.append(alarm_event)
                            uow.alarm_event_records.update(alarm_record)
                            uow.commit()

                    except Exception as e:
                        logger.error(f'Failed to process expired alarm '
                                     f'{alarm_id}: {str(e)}')

        except Exception as e:
            logger.error(f'Error checking expired alarms: {str(e)}')
