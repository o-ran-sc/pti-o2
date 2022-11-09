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

import uuid as uuid

from o2common.service import unit_of_work
from o2common.views.pagination_view import Pagination
from o2common.views.view import gen_filter, check_filter
from o2ims.views.alarm_dto import SubscriptionDTO
from o2ims.domain.alarm_obj import AlarmSubscription, AlarmEventRecord

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

    check_filter(AlarmEventRecord, subscriptionDto['filter'])
    sub_uuid = str(uuid.uuid4())
    subscription = AlarmSubscription(
        sub_uuid, subscriptionDto['callback'],
        subscriptionDto['consumerSubscriptionId'],
        subscriptionDto['filter'])
    with uow:
        uow.alarm_subscriptions.add(subscription)
        uow.commit()
        first = uow.alarm_subscriptions.get(sub_uuid)
        return first.serialize()


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.alarm_subscriptions.delete(subscriptionId)
        uow.commit()
    return True
