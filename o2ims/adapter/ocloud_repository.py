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

from typing import List, Tuple

from o2ims.domain import ocloud, subscription_obj
from o2ims.domain.ocloud_repo import OcloudRepository, ResourceTypeRepository,\
    ResourcePoolRepository, ResourceRepository, DeploymentManagerRepository
from o2ims.domain.subscription_repo import SubscriptionRepository
from o2common.helper import o2logging
logger = o2logging.get_logger(__name__)


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

    def _list(self, *args) -> List[ocloud.Ocloud]:
        return self.session.query(ocloud.Ocloud).filter(*args).order_by(
            'oCloudId')

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

    def _get_by_name(self, resource_type_name) -> ocloud.ResourceType:
        return self.session.query(ocloud.ResourceType).filter_by(
            name=resource_type_name).first()

    def _list(self, *args, **kwargs) -> Tuple[int, List[ocloud.ResourceType]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(ocloud.ResourceType).filter(
            *args).order_by('resourceTypeId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

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

    def _list(self, *args, **kwargs) -> Tuple[int, List[ocloud.ResourcePool]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(ocloud.ResourcePool).filter(
            *args).order_by('resourcePoolId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, resource_pool: ocloud.ResourcePool):
        self.session.add(resource_pool)

    def _delete(self, resource_pool_id):
        self.session.query(ocloud.ResourcePool).filter_by(
            resourcePoolId=resource_pool_id).delete()


class ResourceSqlAlchemyRepository(ResourceRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, resource: ocloud.Resource):
        self.session.add(resource)

    def _get(self, resource_id) -> ocloud.Resource:
        # return self.session.query(ocloud.Resource).filter_by(
        #     resourceId=resource_id).first()
        # topq = uow.session.query(orm.resource).filter(
        #     orm.resource.c.resourceId == resourceId).\
        #     cte('cte', recursive=True)
        # bootomq = uow.session.query(orm.resource).join(
        #     topq, orm.resource.c.parentId == topq.c.resourceId)
        # res = uow.session.query(topq.union(bootomq))
        def recursive(id):
            res = self.session.query(ocloud.Resource).filter_by(
                resourceId=id).first()
            if res is not None:
                query = self.session.query(ocloud.Resource).filter_by(
                    parentId=res.resourceId)
                children = []
                for r in query:
                    child = recursive(r.resourceId)
                    children.append(child)
                res.set_children(children)
            return res
        return recursive(resource_id)

    def _list(self, resourcepool_id, *args, **kwargs) -> \
            Tuple[int, List[ocloud.Resource]]:
        if 'sort' in kwargs:
            kwargs.pop('sort')
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        args1 = args + (ocloud.Resource.resourcePoolId == resourcepool_id,)
        result = self.session.query(ocloud.Resource).filter(
            *args1).order_by('resourceId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, resource: ocloud.Resource):
        self.session.add(resource)

    def _delete(self, resource_id):
        self.session.query(ocloud.Resource).filter_by(
            resourceId=resource_id).delete()


class DeploymentManagerSqlAlchemyRepository(DeploymentManagerRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, deployment_manager: ocloud.DeploymentManager):
        self.session.add(deployment_manager)

    def _get(self, deployment_manager_id) -> ocloud.DeploymentManager:
        return self.session.query(ocloud.DeploymentManager).filter_by(
            deploymentManagerId=deployment_manager_id).first()

    def _list(self, *args, **kwargs) -> Tuple[int,
                                              List[ocloud.DeploymentManager]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(ocloud.DeploymentManager).filter(
            *args).order_by('deploymentManagerId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, deployment_manager: ocloud.DeploymentManager):
        self.session.add(deployment_manager)

    def _delete(self, deployment_manager_id):
        self.session.query(ocloud.DeploymentManager).filter_by(
            deploymentManagerId=deployment_manager_id).delete()


class SubscriptionSqlAlchemyRepository(SubscriptionRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, subscription: subscription_obj.Subscription):
        self.session.add(subscription)

    def _get(self, subscription_id) -> subscription_obj.Subscription:
        return self.session.query(subscription_obj.Subscription).filter_by(
            subscriptionId=subscription_id).first()

    def _list(self, *args, **kwargs) -> \
            Tuple[int, List[subscription_obj.Subscription]]:
        size = kwargs.pop('limit') if 'limit' in kwargs else None
        offset = kwargs.pop('start') if 'start' in kwargs else 0

        result = self.session.query(subscription_obj.Subscription).filter(
            *args).order_by('subscriptionId')
        count = result.count()
        if size is not None and size != -1:
            return (count, result.limit(size).offset(offset))
        return (count, result)

    def _update(self, subscription: subscription_obj.Subscription):
        self.session.add(subscription)

    def _delete(self, subscription_id):
        self.session.query(subscription_obj.Subscription).filter_by(
            subscriptionId=subscription_id).delete()
