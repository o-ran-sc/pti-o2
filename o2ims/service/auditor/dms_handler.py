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

from o2ims.domain.stx_object import StxGenericModel
# from dataclasses import asdict
# from typing import List, Dict, Callable, Type
# TYPE_CHECKING
from o2ims.domain import commands
from o2common.service.unit_of_work import AbstractUnitOfWork
from o2ims.domain.resource_type import MismatchedModel
from o2ims.domain.ocloud import DeploymentManager
from o2common.config import config
# if TYPE_CHECKING:
#     from . import unit_of_work

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class InvalidResourceType(Exception):
    pass


def update_dms(
    cmd: commands.UpdateDms,
    uow: AbstractUnitOfWork
):
    stxobj = cmd.data
    with uow:
        dms = uow.deployment_managers.get(stxobj.id)
        if not dms:
            logger.info("add dms:" + stxobj.name
                        + " update_at: " + str(stxobj.updatetime)
                        + " id: " + str(stxobj.id)
                        + " hash: " + str(stxobj.hash))
            # ocloud = uow.oclouds.get(cmd.parent.oCloudId)
            localmodel = create_by(stxobj, cmd.parentid)
            uow.deployment_managers.add(localmodel)

            logger.info("Add a dms: " + stxobj.id
                        + ", name: " + stxobj.name)
        else:
            localmodel = dms
            if is_outdated(localmodel, stxobj):
                logger.info("update a dms:" + stxobj.name
                            + " update_at: " + str(stxobj.updatetime)
                            + " id: " + str(stxobj.id)
                            + " hash: " + str(stxobj.hash))
                update_by(localmodel, stxobj, cmd.parentid)
                uow.deployment_managers.update(localmodel)

            logger.info("Update a dms: " + stxobj.id
                        + ", name: " + stxobj.name)
        uow.commit()


def is_outdated(ocloud: DeploymentManager, stxobj: StxGenericModel):
    # if stxobj.updatetime:
    #     return True if Ocloud.updatetime < stxobj.updatetime else False
    # else:
    return True if ocloud.hash != stxobj.hash else False


def create_by(stxobj: StxGenericModel, parentid: str) -> DeploymentManager:
    dmsendpoint = config.get_api_url() +\
                  config.get_o2dms_api_base() + "/" + stxobj.id
    description = "A DMS"
    ocloudid = parentid
    supportedLocations = ''
    capabilities = ''
    capacity = ''
    localmodel = DeploymentManager(
        stxobj.id, stxobj.name, ocloudid, dmsendpoint, description,
        supportedLocations, capabilities, capacity)
    localmodel.createtime = stxobj.createtime
    localmodel.updatetime = stxobj.updatetime
    localmodel.hash = stxobj.hash

    return localmodel


def update_by(target: DeploymentManager, stxobj: StxGenericModel,
              parentid: str) -> None:
    if target.deploymentManagerId != stxobj.id:
        raise MismatchedModel("Mismatched Id")
    target.name = stxobj.name
    target.createtime = stxobj.createtime
    target.updatetime = stxobj.updatetime
    # ocloud.content = stxobj.content
    target.hash = stxobj.hash
    target.oCloudId = parentid
    target.version_number = target.version_number + 1
