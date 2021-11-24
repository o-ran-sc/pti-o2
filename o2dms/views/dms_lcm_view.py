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
from o2common.service import unit_of_work
from o2ims.adapter.orm import deploymentmanager
from o2dms.adapter.orm import nfDeploymentDesc
from o2dms.views.dms_dto import DmsLcmNfDeploymentDescriptorDTO
from o2dms.domain.dms import NfDeploymentDesc


def deployment_managers(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(deploymentmanager))
    return [dict(r) for r in res]


def deployment_manager_one(deploymentManagerId: str,
                           uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(deploymentmanager).where(
            deploymentmanager.c.deploymentManagerId == deploymentManagerId))
        first = res.first()
    return None if first is None else dict(first)


def lcm_nfdeploymentdesc_list(deploymentManagerID: str,
                              uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfDeploymentDesc).where(
            nfDeploymentDesc.c.deploymentManagerId == deploymentManagerID))
    return [dict(r) for r in res]


def lcm_nfdeploymentdesc_one(nfdeploymentdescriptorid: str,
                             deploymentManagerID: str,
                             uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfDeploymentDesc).where(
            nfDeploymentDesc.c.deploymentManagerId == deploymentManagerID,
            nfDeploymentDesc.c.id == nfdeploymentdescriptorid))
        first = res.first()
    return None if first is None else dict(first)


def lcm_nfdeploymentdesc_create(
        deploymentManagerId: str,
        input: DmsLcmNfDeploymentDescriptorDTO.
        NfDeploymentDescriptor_create,
        uow: unit_of_work.AbstractUnitOfWork):

    id = str(uuid.uuid4())
    entity = NfDeploymentDesc(
        id, input['name'], deploymentManagerId, input['description'],
        input['inputParams'], input['outputParams'])
    with uow:
        uow.nfdeployment_descs.add(entity)
        uow.commit()
    return entity.id


def lcm_nfdeploymentdesc_update(
        input: DmsLcmNfDeploymentDescriptorDTO.NfDeploymentDescriptor_update,
        uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        entity = uow.nfdeployment_descs.get(input.id)
        entity.name = input['name']
        entity.description = input['description']
        entity.inputParams = input['inputParams']
        entity.outputParams = input['outputParams']
        uow.nfdeployment_descs.add(entity)
        uow.commit()
    return True


def lcm_nfdeploymentdesc_delete(
        nfdeploymentdescriptorid: str, uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        uow.nfdeployment_descs.delete(nfdeploymentdescriptorid)
        uow.commit()
    return True
