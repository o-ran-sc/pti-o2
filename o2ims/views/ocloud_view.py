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
from o2ims.views.ocloud_dto import SubscriptionDTO, ConfigurationDTO
from o2ims.domain.subscription_obj import Subscription
from o2ims.domain.configuration_obj import Configuration


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


def configurations(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.configurations.list()
    return [r.serialize() for r in li]


def configuration_one(configurationId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.configurations.get(configurationId)
        return first.serialize() if first is not None else None


def configuration_create(configurationDto: ConfigurationDTO.configuration,
                         bus: messagebus.MessageBus):

    conf_uuid = str(uuid.uuid4())
    configuration = Configuration(
        conf_uuid, configurationDto['callback'], configurationDto['conftype'])
    with bus.uow as uow:
        uow.configurations.add(configuration)
        logging.debug('before event length {}'.format(
            len(configuration.events)))
        configuration.events.append(events.ConfigurationChanged(
            conf_uuid,
            datetime.now()))
        logging.debug('after event length {}'.format(
            len(configuration.events)))
        uow.commit()
    _handle_events(bus)
    return {"configurationId": conf_uuid}


def configuration_delete(configurationId: str,
                         uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.configurations.delete(configurationId)
        uow.commit()
    return True


def _handle_events(bus: messagebus.MessageBus):
    # handle events
    events = bus.uow.collect_new_events()
    for event in events:
        bus.handle(event)
    return True
