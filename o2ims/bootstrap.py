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

import inspect
from typing import Callable
from o2ims.adapter import orm, redis_eventpublisher
from o2ims.adapter.notifications import AbstractNotifications,\
    SmoO2Notifications

from o2ims.service import handlers, messagebus, unit_of_work
from o2ims.adapter.unit_of_work import SqlAlchemyUnitOfWork
from o2ims.adapter.clients import orm_stx


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = SqlAlchemyUnitOfWork(),
    notifications: AbstractNotifications = None,
    publish: Callable = redis_eventpublisher.publish,
) -> messagebus.MessageBus:

    if notifications is None:
        notifications = SmoO2Notifications()

    if start_orm:
        orm_stx.start_o2ims_stx_mappers(uow)
        with uow:
            # get default engine if uow is by default
            engine = uow.session.get_bind()
            orm.start_o2ims_mappers(engine)

    dependencies = {"uow": uow, "notifications": notifications,
                    "publish": publish}
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies)
            for handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
