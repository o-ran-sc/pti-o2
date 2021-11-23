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
from o2ims.domain.resource_type import InvalidOcloudState
from o2ims.domain.resource_type import MismatchedModel
from o2ims.domain.ocloud import Ocloud
from o2common.config import config
# if TYPE_CHECKING:
#     from . import unit_of_work

from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


class InvalidResourceType(Exception):
    pass


def update_ocloud(
    cmd: commands.UpdateOCloud,
    uow: AbstractUnitOfWork
):
    stxobj = cmd.data
    with uow:
        oclouds = uow.oclouds.list()
        if oclouds and len(oclouds) > 1:
            raise InvalidOcloudState("More than 1 ocloud is found")
        elif not oclouds or len(oclouds) == 0:
            logger.info("add ocloud:" + stxobj.name
                        + " update_at: " + str(stxobj.updatetime)
                        + " id: " + str(stxobj.id)
                        + " hash: " + str(stxobj.hash))
            entry = create_by(stxobj)
            uow.oclouds.add(entry)

            logger.info("Add the ocloud: " + stxobj.id
                        + ", name: " + stxobj.name)
        else:
            localmodel = oclouds.pop()
            if is_outdated(localmodel, stxobj):
                logger.info("update ocloud:" + stxobj.name
                            + " update_at: " + str(stxobj.updatetime)
                            + " id: " + str(stxobj.id)
                            + " hash: " + str(stxobj.hash))
                update_by(localmodel, stxobj)
                uow.oclouds.update(localmodel)

            logger.info("Update the ocloud: " + stxobj.id
                        + ", name: " + stxobj.name)
        uow.commit()


def is_outdated(ocloud: Ocloud, stxobj: StxGenericModel):
    # if stxobj.updatetime:
    #     return True if Ocloud.updatetime < stxobj.updatetime else False
    # else:
    return True if ocloud.hash != stxobj.hash else False


def create_by(stxobj: StxGenericModel) -> Ocloud:
    imsendpoint = config.get_api_url() + config.get_o2ims_api_base()
    globalcloudId = stxobj.id  # to be updated
    description = "An ocloud"
    ocloud = Ocloud(stxobj.id, stxobj.name, imsendpoint,
                    globalcloudId, description, 1)
    ocloud.createtime = stxobj.createtime
    ocloud.updatetime = stxobj.updatetime
    ocloud.hash = stxobj.hash

    return ocloud


def update_by(ocloud: Ocloud, stxobj: StxGenericModel) -> None:
    if ocloud.oCloudId != stxobj.id:
        raise MismatchedModel("More than 1 ocloud found")
    ocloud.name = stxobj.name
    ocloud.createtime = stxobj.createtime
    ocloud.updatetime = stxobj.updatetime
    # ocloud.content = stxobj.content
    ocloud.hash = stxobj.hash
    ocloud.version_number = ocloud.version_number + 1
