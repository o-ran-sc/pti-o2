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

import logging
import uuid
from datetime import datetime

from o2common.service import unit_of_work, messagebus
from o2ims.domain import events
from o2ims.views.ocloud_dto import RegistrationDTO, SubscriptionDTO
from o2ims.domain.subscription_obj import Registration, Subscription


def oclouds(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.oclouds.list()
    return [r.serialize() for r in li]


def ocloud_one(ocloudid: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.oclouds.get(ocloudid)
        return first.serialize() if first is not None else None


def resource_types(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.resource_types.list()
    return [r.serialize() for r in li]


def resource_type_one(resourceTypeId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resource_types.get(resourceTypeId)
        return first.serialize() if first is not None else None


def resource_pools(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.resource_pools.list()
    return [r.serialize() for r in li]


def resource_pool_one(resourcePoolId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resource_pools.get(resourcePoolId)
        return first.serialize() if first is not None else None


def resources(resourcePoolId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.resources.list(resourcePoolId)
    return [r.serialize() for r in li]


def resource_one(resourceId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.resources.get(resourceId)
        return first.serialize() if first is not None else None


def deployment_managers(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.deployment_managers.list()
    return [r.serialize() for r in li]


def deployment_manager_one(deploymentManagerId: str,
                           uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.deployment_managers.get(deploymentManagerId)
        return first.serialize() if first is not None else None


def subscriptions(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.subscriptions.list()
    return [r.serialize() for r in li]


def subscription_one(subscriptionId: str,
                     uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.subscriptions.get(subscriptionId)
        return first.serialize() if first is not None else None


def subscription_create(subscriptionDto: SubscriptionDTO.subscription,
                        uow: unit_of_work.AbstractUnitOfWork):

    sub_uuid = str(uuid.uuid4())
    subscription = Subscription(
        sub_uuid, subscriptionDto['callback'],
        subscriptionDto['consumerSubscriptionId'],
        subscriptionDto['filter'])
    with uow:
        uow.subscriptions.add(subscription)
        uow.commit()
    return {"subscriptionId": sub_uuid}


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.subscriptions.delete(subscriptionId)
        uow.commit()
    return True


def registrations(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.registrations.list()
    return [r.serialize() for r in li]


def registration_one(registrationId: str,
                     uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.registrations.get(registrationId)
        return first.serialize() if first is not None else None


def registration_create(registrationDto: RegistrationDTO.registration,
                        bus: messagebus.MessageBus):

    reg_uuid = str(uuid.uuid4())
    registration = Registration(
        reg_uuid, registrationDto['callback'])
    with bus.uow as uow:
        uow.registrations.add(registration)
        logging.debug('before event length {}'.format(
            len(registration.events)))
        registration.events.append(events.RegistrationChanged(
            reg_uuid,
            datetime.now()))
        logging.debug('after event length {}'.format(len(registration.events)))
        uow.commit()
    _handle_events(bus)
    return {"registrationId": reg_uuid}


def registration_delete(registrationId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.registrations.delete(registrationId)
        uow.commit()
    return True


def _handle_events(bus: messagebus.MessageBus):
    # handle events
    events = bus.uow.collect_new_events()
    for event in events:
        bus.handle(event)
    return True
