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

from retry import retry
import inspect
from typing import Callable, Optional

from o2common.adapter.notifications import AbstractNotifications,\
    NoneNotifications
from o2common.adapter import redis_eventpublisher
from o2common.service import unit_of_work
from o2common.service import messagebus

from o2app.service import handlers
from o2app.adapter.unit_of_work import SqlAlchemyUnitOfWork

from o2ims.adapter import orm as o2ims_orm
from o2dms.adapter import orm as o2dms_orm


from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


@retry(tries=100, delay=2, backoff=1)
def wait_for_db_ready(engine):
    # wait for db up
    logger.info("Wait for DB ready ...")
    engine.connect()
    logger.info("DB is ready")


def bootstrap(
    start_orm: bool = True,
    uow: unit_of_work.AbstractUnitOfWork = SqlAlchemyUnitOfWork(),
    notifications: Optional[AbstractNotifications] = None,
    publish: Callable = redis_eventpublisher.publish,
) -> messagebus.MessageBus:
    """
    Bootstrap the application with dependencies.
    """
    notifications = notifications or NoneNotifications()

    if start_orm:
        with uow:
            engine = uow.session.get_bind()
            wait_for_db_ready(engine)
            o2ims_orm.start_o2ims_mappers(engine)
            o2dms_orm.start_o2dms_mappers(engine)

    dependencies = {
        "uow": uow,
        "notifications": notifications,
        "publish": publish
    }
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

    bus = messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )
    messagebus.MessageBus.set_instance(bus)
    return bus


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
