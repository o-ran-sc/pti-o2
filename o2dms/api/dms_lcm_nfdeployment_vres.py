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
from o2common.service import unit_of_work
from o2dms.adapter.orm import nfOCloudVResource
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


def lcm_nfocloudvresource_list(
        nfDeploymentId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfOCloudVResource).where(
            nfOCloudVResource.c.nfDeploymentId == nfDeploymentId))
    return [dict(r) for r in res]


def lcm_nfocloudvresource_one(
        ocloudvresourceId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(nfOCloudVResource).where(
            nfOCloudVResource.c.id == ocloudvresourceId))
        first = res.first()
    return None if first is None else dict(first)
