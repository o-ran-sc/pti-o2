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

from o2ims.domain import ocloud, subscription_obj, configuration_obj
from o2ims.domain.ocloud_repo import OcloudRepository, ResourceTypeRepository,\
    ResourcePoolRepository, ResourceRepository, DeploymentManagerRepository
from o2ims.domain.subscription_repo import SubscriptionRepository
from o2ims.domain.configuration_repo import ConfigurationRepository
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

    def _list(self) -> List[ocloud.Ocloud]:
        return self.session.query(ocloud.Ocloud)

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
        return self.session.query(ocloud.ResourceType)

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
        return self.session.query(ocloud.ResourcePool)

    def _update(self, resourcePool: ocloud.ResourcePool):
        self.session.add(resourcePool)


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

    def _list(self, resourcepool_id) -> List[ocloud.Resource]:
        return self.session.query(ocloud.Resource).filter_by(
            resourcePoolId=resourcepool_id)

    def _update(self, resource: ocloud.Resource):
        self.session.add(resource)


class DeploymentManagerSqlAlchemyRepository(DeploymentManagerRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, deployment_manager: ocloud.DeploymentManager):
        self.session.add(deployment_manager)

    def _get(self, deployment_manager_id) -> ocloud.DeploymentManager:
        return self.session.query(ocloud.DeploymentManager).filter_by(
            deploymentManagerId=deployment_manager_id).first()

    def _list(self) -> List[ocloud.DeploymentManager]:
        return self.session.query(ocloud.DeploymentManager)

    def _update(self, deployment_manager: ocloud.DeploymentManager):
        self.session.add(deployment_manager)


class SubscriptionSqlAlchemyRepository(SubscriptionRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, subscription: subscription_obj.Subscription):
        self.session.add(subscription)

    def _get(self, subscription_id) -> subscription_obj.Subscription:
        return self.session.query(subscription_obj.Subscription).filter_by(
            subscriptionId=subscription_id).first()

    def _list(self) -> List[subscription_obj.Subscription]:
        return self.session.query(subscription_obj.Subscription)

    def _update(self, subscription: subscription_obj.Subscription):
        self.session.add(subscription)

    def _delete(self, subscription_id):
        self.session.query(subscription_obj.Subscription).filter_by(
            subscriptionId=subscription_id).delete()


class ConfigurationSqlAlchemyRepository(ConfigurationRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, configuration: configuration_obj.Configuration):
        self.session.add(configuration)

    def _get(self, configuration_id) -> configuration_obj.Configuration:
        return self.session.query(configuration_obj.Configuration).filter_by(
            configurationId=configuration_id).first()

    def _list(self) -> List[configuration_obj.Configuration]:
        return self.session.query(configuration_obj.Configuration)

    def _update(self, configuration: configuration_obj.Configuration):
        self.session.add(configuration)

    def _delete(self, configuration_id):
        self.session.query(configuration_obj.Configuration).filter_by(
            configurationId=configuration_id).delete()
