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

from typing import List
# from o2ims.adapter import orm
from o2ims.domain import ocloud
from o2ims.domain.ocloud_repo import OcloudRepository, ResourceTypeRepository,\
    ResourcePoolRepository, ResourceRepository


class OcloudSqlAlchemyRepository(OcloudRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, ocloud: ocloud.Ocloud):
        self.session.add(ocloud)
        # self.session.add_all(ocloud.deploymentManagers)

    def _get(self, ocloud_id) -> ocloud.Ocloud:
        return self.session.query(ocloud.Ocloud).filter_by(
            oCloudId=ocloud_id).first()

    def _list(self) -> List[ocloud.Ocloud]:
        return self.session.query(ocloud.Ocloud).order_by(
            ocloud.Ocloud.name).all()

    def _update(self, ocloud: ocloud.Ocloud):
        self.session.add(ocloud)


class ResouceTypeSqlAlchemyRepository(ResourceTypeRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, resourceType: ocloud.ResourceType):
        self.session.add(resourceType)

    def _get(self, resource_type_id) -> ocloud.ResourceType:
        return self.session.query(ocloud.ResourceType).filter_by(
            resourceTypeId=resource_type_id).first()

    def _list(self) -> List[ocloud.ResourceType]:
        return self.session.query()

    def _update(self, resourceType: ocloud.ResourceType):
        self.session.add(resourceType)


class ResourcePoolSqlAlchemyRepository(ResourcePoolRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, resourcePool: ocloud.ResourcePool):
        self.session.add(resourcePool)

    def _get(self, resource_pool_id) -> ocloud.ResourcePool:
        return self.session.query(ocloud.ResourcePool).filter_by(
            resourcePoolId=resource_pool_id).first()

    def _list(self) -> List[ocloud.ResourcePool]:
        return self.session.query()

    def _update(self, resourcePool: ocloud.ResourcePool):
        self.session.add(resourcePool)


class ResourceSqlAlchemyRepository(ResourceRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, resource: ocloud.Resource):
        self.session.add(resource)

    def _get(self, resource_id) -> ocloud.Resource:
        return self.session.query(ocloud.Resource).filter_by(
            resourceId=resource_id).first()

    def _list(self) -> List[ocloud.Resource]:
        return self.session.query()

    def _update(self, resource: ocloud.Resource):
        self.session.add(resource)
