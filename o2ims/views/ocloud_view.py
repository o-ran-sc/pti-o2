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

from o2ims.adapter.orm import ocloud, resource, resourcetype, \
    resourcepool, deploymentmanager, subscription
from o2common.service import unit_of_work
from o2ims.domain.ocloud import Subscription


def oclouds(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(ocloud))
    return [dict(r) for r in res]


def ocloud_one(ocloudid: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(
            select(ocloud).where(ocloud.c.oCloudId == ocloudid))
        first = res.first()
    return None if first is None else dict(first)


def resource_types(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(resourcetype))
    return [dict(r) for r in res]


def resource_type_one(resourceTypeId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(resourcetype).where(
            resourcetype.c.resourceTypeId == resourceTypeId))
        first = res.first()
    return None if first is None else dict(first)


def resource_pools(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(resourcepool))
    return [dict(r) for r in res]


def resource_pool_one(resourcePoolId: str,
                      uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(resourcepool).where(
            resourcepool.c.resourcePoolId == resourcePoolId))
        first = res.first()
    return None if first is None else dict(first)


def resources(resourcePoolId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(resource).where(
            resource.c.resourcePoolId == resourcePoolId))
    return [dict(r) for r in res]


def resource_one(resourceId: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # topq = uow.session.query(resource).filter(
        #     resource.c.resourceId == resourceId).cte('cte', recursive=True)
        # bootomq = uow.session.query(resource).join(
        #     topq, resource.c.parentId == topq.c.resourceId)
        # res = uow.session.query(topq.union(bootomq))
        # print(res)
        res = uow.session.execute(select(resource).where(
            resource.c.resourceId == resourceId))
        first = res.first()
    return None if first is None else dict(first)


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


def subscriptions(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(subscription))
    return [dict(r) for r in res]


def subscription_one(subscriptionId: str,
                     uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        res = uow.session.execute(select(subscription).where(
            subscription.c.subscriptionId == subscriptionId))
        first = res.first()
    return None if first is None else dict(first)


def subscription_create(subscription: Subscription,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.subscriptions.add(subscription)
        uow.commit()


def subscription_delete(subscriptionId: str,
                        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        uow.subscriptions.delete(subscriptionId)
        uow.commit()
    return True
