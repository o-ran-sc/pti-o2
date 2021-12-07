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

# pylint: disable=unused-argument
from __future__ import annotations
from o2dms.domain.commands import InstallNfDeployment
from typing import Callable

from o2dms.domain import events
from o2common.service.unit_of_work import AbstractUnitOfWork
# if TYPE_CHECKING:
#     from . import unit_of_work

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def publish_nfdeployment_created(
    event: events.NfDeploymentCreated,
    publish: Callable,
):
    publish("NfDeploymentCreated", event)
    logger.debug("published NfDeploymentCreated: {}".format(
        event.NfDeploymentId))


def install_nfdeployment(
    cmd: InstallNfDeployment,
    uow: AbstractUnitOfWork
):
    logger.info("install with NfDeploymentId: {}".format(
        cmd.NfDeploymentId))
