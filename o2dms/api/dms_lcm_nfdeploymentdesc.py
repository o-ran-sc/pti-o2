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

import json
from sqlalchemy import select
import uuid
from o2common.service import unit_of_work
from o2dms.adapter.orm import nfDeploymentDesc
from o2dms.api.dms_dto import DmsLcmNfDeploymentDescriptorDTO
from o2dms.domain.dms import NfDeploymentDesc
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def lcm_nfdeploymentdesc_list(deploymentManagerID: str,
                              uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfDeploymentDesc).where(
            nfDeploymentDesc.c.deploymentManagerId == deploymentManagerID))
    return [dict(r) for r in res]


def lcm_nfdeploymentdesc_one(nfdeploymentdescriptorid: str,
                             uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfDeploymentDesc).where(
            nfDeploymentDesc.c.id == nfdeploymentdescriptorid))
        first = res.first()
    return None if first is None else dict(first)


def _check_duplication(name: str, uow: unit_of_work.AbstractUnitOfWork):
    if uow.nfdeployment_descs.count(name=name) > 0:
        raise Exception(
            "NfDeploymentDescriptor with name {} exists already".format(name))


def lcm_nfdeploymentdesc_create(
        deploymentManagerId: str,
        input: DmsLcmNfDeploymentDescriptorDTO.
        NfDeploymentDescriptor_create,
        uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        _check_duplication(input['name'], uow)
        id = str(uuid.uuid4())
        inputParams = input.get('inputParams', {})
        outputParams = input.get('outputParams', {})
        entity = NfDeploymentDesc(
            id, input['name'], deploymentManagerId, input['description'],
            inputParams, outputParams,
            input['artifactRepoUrl'], input['artifactName'])
        _nfdeploymentdesc_validate(entity)
        uow.nfdeployment_descs.add(entity)
        uow.commit()
    return id


def _nfdeploymentdesc_validate(desc: NfDeploymentDesc):
    try:
        if desc.inputParams:
            json.loads(desc.inputParams)
        if desc.outputParams:
            json.loads(desc.outputParams)
        if not desc.deploymentManagerId:
            raise Exception("Invalid deploymentManager Id")
        if not desc.artifactRepoUrl:
            raise Exception("Invalid artifactRepoUrl")
        if not desc.artifactName:
            raise Exception("Invalid artifactName")
        return
    except json.decoder.JSONDecodeError as e:
        logger.debug("NfDeploymentDesc json error with: %s" % (str(e)))
        raise e
    except Exception as e:
        logger.debug("NfDeploymentDesc validate error with: %s" % (str(e)))
        raise e


def lcm_nfdeploymentdesc_update(
        nfdeploymentdescriptorid: str,
        input: DmsLcmNfDeploymentDescriptorDTO.NfDeploymentDescriptor_update,
        uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        entity = uow.nfdeployment_descs.get(nfdeploymentdescriptorid)
        entity.name = input['name']
        entity.description = input['description']
        entity.inputParams = input['inputParams']
        entity.outputParams = input['outputParams']
        entity.artifactRepoUrl = input['artifactRepoUrl']
        entity.artifactName = input['artifactName']
        uow.commit()
    return True


def lcm_nfdeploymentdesc_delete(
        nfdeploymentdescriptorid: str, uow: unit_of_work.AbstractUnitOfWork):

    with uow:
        # check dependency
        _check_dependencies(nfdeploymentdescriptorid, uow)
        uow.nfdeployment_descs.delete(nfdeploymentdescriptorid)
        uow.commit()
    return True


def _check_dependencies(
    descriptorId: str, uow: unit_of_work.AbstractUnitOfWork
):
    # check if nfdeployment depends on it
    if uow.nfdeployments.count(descriptorId=descriptorId) > 0:
        raise Exception(
            "NfDeployment with descriptorId {} exists".format(
                descriptorId))
