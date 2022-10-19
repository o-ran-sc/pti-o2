# Copyright (C) 2022 Wind River Systems, Inc.
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

# client talking to Stx standalone

from typing import List  # Optional,  Set
import uuid as uuid

# from dcmanagerclient.api import client
# from cgtsclient.client import get_client as get_stx_client
# from cgtsclient.exc import EndpointException
# from dcmanagerclient.api.client import client as get_dc_client
from fmclient.client import get_client as get_fm_client
from fmclient.common.exceptions import HTTPNotFound

from o2common.service.client.base_client import BaseClient
from o2common.config import config
from o2ims.domain import alarm_obj as alarmModel
from o2ims.domain.resource_type import ResourceTypeEnum
from o2app.adapter import unit_of_work

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


CGTSCLIENT_ENDPOINT_ERROR_MSG = \
    'Must provide Keystone credentials or user-defined endpoint and token'


class StxAlarmClient(BaseClient):
    def __init__(self, uow: unit_of_work.AbstractUnitOfWork, driver=None):
        super().__init__()
        self.driver = driver if driver else StxFaultClientImp()
        self.uow = uow

    def _get(self, id) -> alarmModel.FaultGenericModel:
        return self.driver.getAlarmInfo(id)

    def _list(self, **filters) -> List[alarmModel.FaultGenericModel]:
        # filters['resourcetypeid']
        newmodels = self.driver.getAlarmList(**filters)
        uow = self.uow
        exist_alarms = {}
        with uow:
            rs = uow.session.execute(
                '''
                SELECT "alarmEventRecordId"
                FROM "alarmEventRecord"
                WHERE "perceivedSeverity" != :perceived_severity_enum
                ''',
                dict(perceived_severity_enum=alarmModel.PerceivedSeverityEnum.
                     CLEARED)
            )
            for row in rs:
                id = row[0]
                # logger.debug('Exist alarm: ' + id)
                exist_alarms[id] = False

        ret = []
        for m in newmodels:
            try:
                if exist_alarms[m.id]:
                    ret.append(m)
                    exist_alarms[m.id] = True
            except KeyError:
                logger.debug('alarm new: ' + m.id)
                ret.append(m)

        for alarm in exist_alarms:
            logger.debug('exist alarm: ' + alarm)
            if exist_alarms[alarm]:
                # exist alarm is active
                continue
            event = self._get(alarm)
            ret.append(event)

        return ret

    def _set_stx_client(self):
        pass


class StxEventClient(BaseClient):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver if driver else StxFaultClientImp()

    def _get(self, id) -> alarmModel.FaultGenericModel:
        return self.driver.getEventInfo(id)

    def _list(self, **filters) -> List[alarmModel.FaultGenericModel]:
        return self.driver.getEventList(**filters)

    def _set_stx_client(self):
        pass


# internal driver which implement client call to Stx Fault Management instance
class StxFaultClientImp(object):
    def __init__(self, fm_client=None):
        super().__init__()
        self.fmclient = fm_client if fm_client else self.getFmClient()
        # if subcloud_id is not None:
        # self.stxclient = self.getSubcloudClient(subcloud_id)

    def getFmClient(self):
        os_client_args = config.get_fm_access_info()
        config_client = get_fm_client(1, **os_client_args)
        return config_client

    def getAlarmList(self, **filters) -> List[alarmModel.FaultGenericModel]:
        alarms = self.fmclient.alarm.list(expand=True)
        if len(alarms) == 0:
            return []
        logger.debug('alarm 1:' + str(alarms[0].to_dict()))
        # [print('alarm:' + str(alarm.to_dict())) for alarm in alarms if alarm]
        return [alarmModel.FaultGenericModel(
            ResourceTypeEnum.PSERVER, self._alarmconverter(alarm))
            for alarm in alarms if alarm]

    def getAlarmInfo(self, id) -> alarmModel.FaultGenericModel:
        try:
            alarm = self.fmclient.alarm.get(id)
            logger.debug('get alarm id ' + id + ':' + str(alarm.to_dict()))
            # print(alarm.to_dict())
        except HTTPNotFound:
            event = self.fmclient.event_log.get(id)
            return alarmModel.FaultGenericModel(
                ResourceTypeEnum.PSERVER, self._eventconverter(event, True))
        return alarmModel.FaultGenericModel(
            ResourceTypeEnum.PSERVER, self._alarmconverter(alarm))

    def getEventList(self, **filters) -> List[alarmModel.FaultGenericModel]:
        events = self.fmclient.event_log.list(alarms=True, expand=True)
        logger.debug('event 1:' + str(events[0].to_dict()))
        # [print('alarm:' + str(event.to_dict())) for event in events if event]
        return [alarmModel.FaultGenericModel(
            ResourceTypeEnum.PSERVER, self._eventconverter(event))
            for event in events if event]

    def getEventInfo(self, id) -> alarmModel.FaultGenericModel:
        event = self.fmclient.event_log.get(id)
        logger.debug('get event id ' + id + ':' + str(event.to_dict()))
        # print(event.to_dict())
        return alarmModel.FaultGenericModel(
            ResourceTypeEnum.PSERVER, self._eventconverter(event))

    @ staticmethod
    def _alarmconverter(alarm):
        # setattr(alarm, 'alarm_def_id', uuid.uuid3(
        #         uuid.NAMESPACE_URL, alarm.alarm_id))
        setattr(alarm, 'state', alarm.alarm_state)
        setattr(alarm, 'event_log_type', alarm.alarm_type)
        setattr(alarm, 'event_log_id', alarm.alarm_id)

        setattr(alarm, 'alarm_def_id', uuid.uuid3(
                uuid.NAMESPACE_URL, alarm.alarm_id))
        setattr(alarm, 'probable_cause_id', uuid.uuid3(
                uuid.NAMESPACE_URL, alarm.probale_cause))
        return alarm

    @ staticmethod
    def _eventconverter(event, clear=False):
        setattr(event, 'alarm_id', event.event_log_id)
        setattr(event, 'alarm_type', event.event_log_type)
        if clear:
            logger.debug('alarm is clear')
            event.state = 'clear'
        setattr(event, 'alarm_def_id', uuid.uuid3(
                uuid.NAMESPACE_URL, event.alarm_id))
        setattr(event, 'probable_cause_id', uuid.uuid3(
                uuid.NAMESPACE_URL, event.probale_cause))
        return event

    @ staticmethod
    def _alarmeventhasher(event, state=''):
        # The event model and the alarm model have different parameter name
        # of the state. alarm model is alarm_state, event model is state.
        status = event.alarm_state if state == '' else state
        return str(hash((event.uuid, event.timestamp, status)))
