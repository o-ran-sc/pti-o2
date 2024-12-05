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

import uuid
import time
import json
from datetime import datetime
from unittest.mock import MagicMock
from typing import Callable

from o2common.service.watcher import worker
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2common.service.client.base_client import BaseClient
from o2common.service.watcher.base import BaseWatcher, WatcherTree
from o2common.service import messagebus
from o2common.config import config

from o2ims.domain.resource_type import ResourceTypeEnum
from o2ims.domain import alarm_obj
from o2ims.domain import commands
from o2ims.views import alarm_view
from o2ims.service.watcher.alarm_watcher import AlarmWatcher

from o2app.service import handlers
from o2app import bootstrap


def test_new_alarm_event_record():
    alarm_event_record_id1 = str(uuid.uuid4())
    alarm_event_record = alarm_obj.AlarmEventRecord(
        alarm_event_record_id1, '',
        '', '', '', alarm_obj.PerceivedSeverityEnum.CRITICAL)
    assert alarm_event_record_id1 is not None and \
        alarm_event_record.alarmEventRecordId == alarm_event_record_id1


def test_view_alarm_event_records(mock_uow):
    session, uow = mock_uow

    alarm_event_record_id1 = str(uuid.uuid4())
    alarm_event_record1 = MagicMock()
    alarm_event_record1.serialize.return_value = {
        "alarmEventRecordId": alarm_event_record_id1}

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [alarm_event_record1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    result = alarm_view.alarm_event_records(uow)
    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].get("alarmEventRecordId")) == alarm_event_record_id1


def test_view_alarm_event_record_one(mock_uow):
    session, uow = mock_uow

    alarm_event_record_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    alarm_event_record1 = alarm_view.alarm_event_record_one(
        alarm_event_record_id1, uow)
    assert alarm_event_record1 is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "alarmEventRecordId": alarm_event_record_id1}

    alarm_event_record1 = alarm_view.alarm_event_record_one(
        alarm_event_record_id1, uow)
    assert str(alarm_event_record1.get(
        "alarmEventRecordId")) == alarm_event_record_id1


def test_view_alarm_subscriptions(mock_uow):
    session, uow = mock_uow

    subscription_id1 = str(uuid.uuid4())
    sub1 = MagicMock()
    sub1.serialize.return_value = {
        "alarmSubscriptionId": subscription_id1,
    }

    order_by = MagicMock()
    order_by.count.return_value = 1
    order_by.limit.return_value.offset.return_value = [sub1]
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    result = alarm_view.subscriptions(uow)
    assert result['count'] == 1
    ret_list = result['results']
    assert str(ret_list[0].get("alarmSubscriptionId")) == subscription_id1


def test_view_alarm_subscription_one(mock_uow):
    session, uow = mock_uow

    subscription_id1 = str(uuid.uuid4())
    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = None

    # Query return None
    subscription_res = alarm_view.subscription_one(
        subscription_id1, uow)
    assert subscription_res is None

    session.return_value.query.return_value.filter_by.return_value.first.\
        return_value.serialize.return_value = {
            "alarmSubscriptionId": subscription_id1,
        }

    subscription_res = alarm_view.subscription_one(
        subscription_id1, uow)
    assert str(subscription_res.get(
        "alarmSubscriptionId")) == subscription_id1


def test_flask_get_list(mock_flask_uow):
    session, app = mock_flask_uow
    order_by = MagicMock()
    order_by.count.return_value = 0
    order_by.limit.return_value.offset.return_value = []
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    with app.test_client() as client:
        # Get list and return empty list
        ##########################
        resp = client.get(apibase+"/alarms")
        assert resp.get_data() == b'[]\n'

        resp = client.get(apibase+"/alarmSubscriptions")
        assert resp.get_data() == b'[]\n'


def test_flask_get_one(mock_flask_uow):
    session, app = mock_flask_uow

    session.return_value.query.return_value.filter_by.return_value.\
        first.return_value = None
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    with app.test_client() as client:
        # Get one and return 404
        ###########################
        alarm_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/alarms/"+alarm_id1)
        assert resp.status_code == 404

        sub_id1 = str(uuid.uuid4())
        resp = client.get(apibase+"/alarmSubscriptions/"+sub_id1)
        assert resp.status_code == 404


def test_flask_post(mock_flask_uow, mappers):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    order_by = MagicMock()
    order_by.count.return_value = 0
    order_by.limit.return_value.offset.return_value = []
    session.return_value.query.return_value.filter.return_value.\
        order_by.return_value = order_by

    with app.test_client() as client:
        session.return_value.execute.return_value = []

        sub_callback = 'http://subscription/callback/url'
        resp = client.post(apibase+'/alarmSubscriptions', json={
            'callback': sub_callback,
            'consumerSubscriptionId': 'consumerSubId1',
            'filter': '(eq,resourceTypeId,xxx)'
        })
        assert resp.status_code == 201
        assert 'alarmSubscriptionId' in resp.get_json()


def test_flask_delete(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    with app.test_client() as client:
        session.return_value.execute.return_value.first.return_value = {}

        subscription_id1 = str(uuid.uuid4())
        resp = client.delete(apibase+"/alarmSubscriptions/"+subscription_id1)
        assert resp.status_code == 200


def test_flask_not_allowed(mock_flask_uow):
    _, app = mock_flask_uow
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    with app.test_client() as client:
        # Testing resource type not support method
        ##########################
        uri = apibase + "/alarms"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.put(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.patch(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'

        # Testing alarm service configuration not support method
        ##########################
        uri = apibase + "/alarmServiceConfiguration"
        resp = client.post(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'
        resp = client.delete(uri)
        assert resp.status == '405 METHOD NOT ALLOWED'


class FakeAlarmClient(BaseClient):
    def __init__(self):
        super().__init__()
        fakeAlarm = alarm_obj.FaultGenericModel(ResourceTypeEnum.OCLOUD)
        fakeAlarm.id = str(uuid.uuid4())
        fakeAlarm.name = 'alarm'
        fakeAlarm.content = json.dumps({})
        fakeAlarm.createtime = datetime.now()
        fakeAlarm.updatetime = datetime.now()
        fakeAlarm.hash = str(hash((fakeAlarm.id, fakeAlarm.updatetime)))
        self.fakeAlarm = fakeAlarm

    def _get(self, id) -> alarm_obj.FaultGenericModel:
        return self.fakeAlarm

    def _list(self):
        return [self.fakeAlarm]

    def _set_stx_client(self):
        pass


# class FakeStxObjRepo(StxObjectRepository):
#     def __init__(self):
#         super().__init__()
#         self.alarms = []

#     def _add(self, alarm: alarm_obj.AlarmEventRecord):
#         self.alarms.append(alarm)

#     def _get(self, alarmid) -> alarm_obj.AlarmEventRecord:
#         filtered = [a for a in self.alarms if a.id == alarmid]
#         return filtered.pop()

#     def _list(self) -> List[alarm_obj.AlarmEventRecord]:
#         return [x for x in self.oclouds]

#     def _update(self, alarm: alarm_obj.AlarmEventRecord):
#         filtered = [a for a in self.alarms if a.id == alarm.id]
#         assert len(filtered) == 1
#         ocloud1 = filtered.pop()
#         ocloud1.update_by(alarm)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=None):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory
        # self.stxobjects = FakeStxObjRepo()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        # self.session.close()

    def _commit(self):
        pass
        # self.session.commit()

    def rollback(self):
        pass
        # self.session.rollback()

    def collect_new_events(self):
        yield
        # return super().collect_new_events()


def create_alarm_fake_bus(uow):
    def update_alarm(
            cmd: commands.UpdateAlarm,
            uow: AbstractUnitOfWork,
            publish: Callable):
        return

    handlers.EVENT_HANDLERS = {}
    handlers.COMMAND_HANDLERS = {
        commands.UpdateAlarm: update_alarm,
    }
    bus = bootstrap.bootstrap(False, uow)
    return bus


def test_probe_new_alarm():
    session = MagicMock()
    session.return_value.execute.return_value = []
    fakeuow = FakeUnitOfWork(session)
    bus = create_alarm_fake_bus(fakeuow)
    fakeClient = FakeAlarmClient()
    alarmwatcher = AlarmWatcher(fakeClient, bus)
    parent = type('obj', (object,), {
        'data': type('obj', (object,), {
            'id': 'test_parent_id',
            'res_pool_id': 'test_res_pool'
        })})
    cmds = alarmwatcher.probe(parent)
    assert cmds is not None
    assert len(cmds) == 1
    assert cmds[0].data.name == "alarm"
    # assert len(fakeuow.stxobjects.oclouds) == 1
    # assert fakeuow.stxobjects.oclouds[0].name == "stx1"


def test_watchers_worker():
    testedworker = worker.PollWorker()

    class FakeAlarmWatcher(BaseWatcher):
        def __init__(self, client: BaseClient,
                     bus: messagebus) -> None:
            super().__init__(client, None)
            self.fakeOcloudWatcherCounter = 0
            self._client = client
            self._bus = bus

        def _targetname(self):
            return "fakealarmwatcher"

        def _probe(self, parent: object = None, tags=None):
            # import pdb; pdb.set_trace()
            self.fakeOcloudWatcherCounter += 1
            # hacking to stop the blocking sched task
            if self.fakeOcloudWatcherCounter > 2:
                testedworker.stop()
            return []

    # fakeRepo = FakeOcloudRepo()
    fakeuow = FakeUnitOfWork()
    bus = create_alarm_fake_bus(fakeuow)

    fakeClient = FakeAlarmClient()
    fakewatcher = FakeAlarmWatcher(fakeClient, bus)

    root = WatcherTree(fakewatcher)

    testedworker.set_interval(1)
    testedworker.add_watcher(root)
    assert fakewatcher.fakeOcloudWatcherCounter == 0

    count1 = fakewatcher.fakeOcloudWatcherCounter
    testedworker.start()
    time.sleep(20)
    assert fakewatcher.fakeOcloudWatcherCounter > count1

    # assumed hacking: probe has stopped the sched task
    count3 = fakewatcher.fakeOcloudWatcherCounter
    time.sleep(3)
    assert fakewatcher.fakeOcloudWatcherCounter == count3


def test_view_alarm_service_configuration(mock_uow):
    session, uow = mock_uow

    # Test the first time call the view will generate the default data
    session.return_value.query.return_value.first.return_value = None
    result = alarm_view.alarm_service_configuration(uow)
    assert result is not None
    assert result.get("retentionPeriod") == 14

    config1 = MagicMock()
    config1.serialize.return_value = {
        "id": 1,
        "retentionPeriod": 30
    }
    session.return_value.query.return_value.first.return_value = config1

    result = alarm_view.alarm_service_configuration(uow)
    assert result is not None
    assert result.get("id") == 1
    assert result.get("retentionPeriod") == 30


def test_view_alarm_service_configuration_update(mock_uow):
    session, uow = mock_uow

    config1 = MagicMock()
    config1.serialize.return_value = {
        "id": 1,
        "retentionPeriod": 60
    }
    session.return_value.query.return_value.first.return_value = config1

    # Test update the config
    update_data = {
        "retentionPeriod": 60
    }
    result = alarm_view.alarm_service_configuration_update(update_data, uow)

    assert result is not None
    assert result.get("id") == 1
    assert result.get("retentionPeriod") == 60
    # Verify the update and commit is called
    session.return_value.query.return_value.first.return_value.\
        retentionPeriod = 60
    assert session.return_value.commit.called


def test_flask_get_alarm_config(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    config1 = MagicMock()
    config1.serialize.return_value = {
        "retentionPeriod": 30
    }

    session.return_value.query.return_value.first.return_value = config1

    with app.test_client() as client:
        resp = client.get(apibase+"/alarmServiceConfiguration")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["retentionPeriod"] == 30


def test_flask_patch_alarm_config(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    config1 = MagicMock()
    config1.serialize.return_value = {
        "retentionPeriod": 60
    }
    session.return_value.query.return_value.first.return_value = config1

    with app.test_client() as client:
        # Test updating retention period
        resp = client.patch(apibase+"/alarmServiceConfiguration", json={
            "retentionPeriod": 60
        })
        assert resp.status_code == 200

        # Test invalid retention period
        resp = client.patch(apibase+"/alarmServiceConfiguration", json={
            "retentionPeriod": -1
        })
        assert resp.status_code == 400


def test_flask_put_alarm_config(mock_flask_uow):
    session, app = mock_flask_uow
    apibase = config.get_o2ims_monitoring_api_base() + '/v1'

    config1 = MagicMock()
    config1.serialize.return_value = {
        "alarmServiceId": "alarm-service-1",
        "retentionPeriod": 60
    }
    session.return_value.query.return_value.first.return_value = config1

    with app.test_client() as client:
        # Test updating retention period
        resp = client.put(apibase+"/alarmServiceConfiguration", json={
            "retentionPeriod": 60
        })
        assert resp.status_code == 200

        # Test invalid retention period
        resp = client.put(apibase+"/alarmServiceConfiguration", json={
            "retentionPeriod": -1
        })
        assert resp.status_code == 400
