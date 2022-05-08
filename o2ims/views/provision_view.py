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
from o2ims.views.provision_dto import SmoEndpointDTO
from o2ims.domain.configuration_obj import Configuration, ConfigurationTypeEnum


def configurations(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        li = uow.configurations.list()
    return [r.serialize_smo() for r in li]


def configuration_one(configurationId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        first = uow.configurations.get(configurationId)
        return first.serialize_smo() if first is not None else None


def configuration_create(configurationDto: SmoEndpointDTO.endpoint,
                         bus: messagebus.MessageBus):

    conf_uuid = str(uuid.uuid4())
    configuration = Configuration(
        conf_uuid, configurationDto['endpoint'], ConfigurationTypeEnum.SMO)
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
    return {"id": conf_uuid}


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
