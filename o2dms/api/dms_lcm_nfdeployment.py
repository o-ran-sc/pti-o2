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

from sqlalchemy import select
import uuid
from o2common.service import messagebus
from o2dms.domain import events
from o2common.service import unit_of_work
from o2dms.adapter.orm import nfDeployment
from o2dms.api.dms_dto import DmsLcmNfDeploymentDTO
from o2dms.domain.dms import NfDeployment
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def lcm_nfdeployment_list(
        deploymentManagerID: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfDeployment).where(
            nfDeployment.c.deploymentManagerId == deploymentManagerID))
    return [dict(r) for r in res]


def lcm_nfdeployment_one(
        nfdeploymentid: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfDeployment).where(
            nfDeployment.c.id == nfdeploymentid))
        first = res.first()
    return None if first is None else dict(first)


def lcm_nfdeployment_create(
        deploymentManagerId: str,
        input: DmsLcmNfDeploymentDTO.
        NfDeployment_create,
        bus: messagebus.MessageBus):

    uow = bus.uow
    with uow:
        _check_duplication(input, uow)
        _check_dependencies(input, uow)
        id = str(uuid.uuid4())
        entity = NfDeployment(
            id, input['name'], deploymentManagerId, input['description'],
            input['descriptorId'], input['parentDeploymentId'])
        uow.nfdeployments.add(entity)

        # publish event
        event = events.NfDeploymentCreated(NfDeploymentId=id)
        uow.commit()
    bus.handle(event)

    return id


def lcm_nfdeployment_update(
        nfdeploymentid: str,
        input: DmsLcmNfDeploymentDTO.NfDeployment_update,
        uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        entity = uow.nfdeployments.get(nfdeploymentid)
        entity.name = input['name']
        entity.description = input['description']
        entity.outputParams = input['parentDeploymentId']
        uow.commit()
    return True


def lcm_nfdeployment_delete(
        nfdeploymentid: str, uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        uow.nfdeployments.delete(nfdeploymentid)
        uow.commit()
    return True


def _check_duplication(
        input: DmsLcmNfDeploymentDTO,
        uow: unit_of_work.AbstractUnitOfWork):
    name = input['name']
    descriptorId = input['descriptorId']
    if uow.nfdeployments.count(name=name) > 0:
        raise Exception(
            "NfDeployment with name {} exists already".format(name))
    if uow.nfdeployments.count(descriptorId=descriptorId) > 0:
        raise Exception(
            "NfDeployment with descriptorId {} exists already".format(
                descriptorId))


def _check_dependencies(
        input: DmsLcmNfDeploymentDTO,
        uow: unit_of_work.AbstractUnitOfWork):
    descriptorId = input['descriptorId']
    if uow.nfdeployment_descs.count(id=descriptorId) == 0:
        raise Exception(
            "NfDeploymentDescriptor with id {} does not exist".format(
                descriptorId))
