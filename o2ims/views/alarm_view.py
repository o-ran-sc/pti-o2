# Copyright (C) 2021-2024 Wind River Systems, Inc.
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

from datetime import datetime
import uuid as uuid

from o2common.service import unit_of_work, messagebus
from o2common.views.view import gen_filter, check_filter
from o2common.views.pagination_view import Pagination
from o2common.views.route_exception import BadRequestException, \
    NotFoundException

from o2ims.domain import events
from o2ims.views.alarm_dto import SubscriptionDTO
from o2ims.domain.alarm_obj import AlarmSubscription, AlarmEventRecord, \
    AlarmNotificationEventEnum, AlarmEventRecordModifications, \
    PerceivedSeverityEnum

from o2common.helper import o2logging
# from o2common.config import config
logger = o2logging.get_logger(__name__)


def alarm_event_records(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(AlarmEventRecord,
                      kwargs['filter']) if 'filter' in kwargs else []
    with uow:
        li = uow.alarm_event_records.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def alarm_event_record_one(alarmEventRecordId: str,
                           uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.alarm_event_records.get(alarmEventRecordId)
        return first.serialize() if first is not None else None


def alarm_event_record_ack(alarmEventRecordId: str,
                           uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        alarm_event_record = uow.alarm_event_records.get(alarmEventRecordId)
        # Check the record does not exist, return None. Otherwise, the
        # acknowledge request will update the record even if it is
        # acknowledged.
        if alarm_event_record is None:
            return None
        alarm_event_record.alarmAcknowledged = True
        alarm_event_record.alarmAcknowledgeTime = datetime.\
            now().strftime("%Y-%m-%dT%H:%M:%S")
        uow.alarm_event_records.update(alarm_event_record)
        uow.commit()

        result = AlarmEventRecordModifications(True)
    return result


def alarm_event_record_clear(alarmEventRecordId: str,
                             uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        alarm_event_record = uow.alarm_event_records.get(alarmEventRecordId)
        if alarm_event_record is None:
            return None
        elif alarm_event_record.perceivedSeverity == \
                PerceivedSeverityEnum.CLEARED:
            raise BadRequestException(
                "Alarm Event Record {} has already been marked as CLEARED."
                .format(alarmEventRecordId))
        alarm_event_record.events.append(events.AlarmEventCleared(
            id=alarm_event_record.alarmEventRecordId,
            notificationEventType=AlarmNotificationEventEnum.CLEAR))

        uow.alarm_event_records.update(alarm_event_record)
        uow.commit()

        result = AlarmEventRecordModifications(
            clear=PerceivedSeverityEnum.CLEARED)
    _handle_events(messagebus.MessageBus.get_instance())
    return result


def _handle_events(bus: messagebus.MessageBus):
    # handle events
    events = bus.uow.collect_new_events()
    for event in events:
        bus.handle(event)
    return True


def subscriptions(uow: unit_of_work.AbstractUnitOfWork, **kwargs):
    pagination = Pagination(**kwargs)
    query_kwargs = pagination.get_pagination()
    args = gen_filter(AlarmSubscription,
                      kwargs['filter']) if 'filter' in kwargs else []
    with uow:
        li = uow.alarm_subscriptions.list_with_count(*args, **query_kwargs)
    return pagination.get_result(li)


def subscription_one(subscriptionId: str,
                     uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.alarm_subscriptions.get(subscriptionId)
        return first.serialize() if first is not None else None


def subscription_create(subscriptionDto: SubscriptionDTO.subscription_create,
                        uow: unit_of_work.AbstractUnitOfWork):
    filter = subscriptionDto.get('filter', '')
    consumer_subs_id = subscriptionDto.get('consumerSubscriptionId', '')

    check_filter(AlarmEventRecord, filter)

    sub_uuid = str(uuid.uuid4())
    subscription = AlarmSubscription(
        sub_uuid, subscriptionDto['callback'],
        consumer_subs_id, filter)
    with uow:
        args = list()
        args.append(getattr(AlarmSubscription, 'callback')
                    == subscriptionDto['callback'])
        args.append(getattr(AlarmSubscription, 'filter') == filter)
        args.append(getattr(AlarmSubscription,
                    'consumerSubscriptionId') == consumer_subs_id)
        count, _ = uow.alarm_subscriptions.list_with_count(*args)
        if count > 0:
            raise BadRequestException("The value of parameters is duplicated")
        uow.alarm_subscriptions.add(subscription)
        uow.commit()
        first = uow.alarm_subscriptions.get(sub_uuid)
        return first.serialize()


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.alarm_subscriptions.get(subscriptionId)
        if not first:
            raise NotFoundException(
                "Alarm Subscription {} not found.".format(subscriptionId))
        uow.alarm_subscriptions.delete(subscriptionId)
        uow.commit()
    return True


def alarm_service_configuration(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.alarm_service_config.get()
        return first.serialize() if first is not None else None


def alarm_service_configuration_update(data: dict,
                                       uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.alarm_service_config.get()
        first.retentionPeriod = data.get('retentionPeriod')
        uow.alarm_service_config.update(first)
        uow.commit()
        return first.serialize()
