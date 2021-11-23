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

import uuid
from flask_restx import Resource

from o2ims.views import ocloud_view, api
from o2common.config import config
from o2ims.domain.ocloud import Subscription
from o2ims.views.ocloud_dto import OcloudDTO, ResourceTypeDTO,\
    ResourcePoolDTO, ResourceDTO, DeploymentManagerDTO, SubscriptionDTO


apibase = config.get_o2ims_api_base()


# ----------  OClouds ---------- #
@api.route("/")
@api.response(404, 'oCloud not found')
class OcloudsListRouter(Resource):
    """Ocloud get endpoint
    O2 interface ocloud endpoint
    """

    ocloud_get = OcloudDTO.ocloud

    @api.marshal_with(ocloud_get)
    def get(self):
        res = ocloud_view.oclouds(uow)
        if len(res) > 0:
            return res[0]
        api.abort(
            404, "oCloud doesn't exist")


# ----------  ResourceTypes ---------- #
@api.route("/resourceTypes")
class ResourceTypesListRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api.marshal_list_with(model)
    def get(self):
        return ocloud_view.resource_types(uow)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def post(self):
    #     api.abort(405)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def put(self):
    #     api.abort(405)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def patch(self):
    #     api.abort(405)

    # @api.doc(response={405: 'Method Not Allowed'})
    # def delete(self):
    #     api.abort(405)


@api.route("/resourceTypes/<resourceTypeID>")
@api.param('resourceTypeID', 'ID of the resource type')
@api.response(404, 'Resource type not found')
class ResourceTypeGetRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api.doc('Get resource type')
    @api.marshal_with(model)
    def get(self, resourceTypeID):
        result = ocloud_view.resource_type_one(resourceTypeID, uow)
        if result is not None:
            return result
        api.abort(
            404, "Resource type {} doesn't exist".format(resourceTypeID))


# ----------  ResourcePools ---------- #
@api.route("/resourcePools")
class ResourcePoolsListRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api.marshal_list_with(model)
    def get(self):
        return ocloud_view.resource_pools(uow)


@api.route("/resourcePools/<resourcePoolID>")
@api.param('resourcePoolID', 'ID of the resource pool')
@api.response(404, 'Resource pool not found')
class ResourcePoolGetRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api.doc('Get resource pool')
    @api.marshal_with(model)
    def get(self, resourcePoolID):
        result = ocloud_view.resource_pool_one(resourcePoolID, uow)
        if result is not None:
            return result
        api.abort(
            404, "Resource pool {} doesn't exist".format(resourcePoolID))


# ----------  Resources ---------- #
@api.route("/resourcePools/<resourcePoolID>/resources")
@api.param('resourcePoolID', 'ID of the resource pool')
class ResourcesListRouter(Resource):

    model = ResourceDTO.resource_list

    @api.marshal_list_with(model)
    def get(self, resourcePoolID):
        return ocloud_view.resources(resourcePoolID, uow)


@api.route("/resourcePools/<resourcePoolID>/resources/<resourceID>")
@api.param('resourcePoolID', 'ID of the resource pool')
@api.param('resourceID', 'ID of the resource')
@api.response(404, 'Resource not found')
class ResourceGetRouter(Resource):

    model = ResourceDTO.resource_get

    @api.doc('Get resource')
    @api.marshal_with(model)
    def get(self, resourcePoolID, resourceID):
        result = ocloud_view.resource_one(resourceID, uow)
        if result is not None:
            return result
        api.abort(404, "Resource {} doesn't exist".format(resourceID))


# ----------  DeploymentManagers ---------- #
@api.route("/deploymentManagers")
class DeploymentManagersListRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api.marshal_list_with(model)
    def get(self):
        return ocloud_view.deployment_managers(uow)


@api.route("/deploymentManagers/<deploymentManagerID>")
@api.param('deploymentManagerID', 'ID of the deployment manager')
@api.response(404, 'Deployment manager not found')
class DeploymentManagerGetRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api.doc('Get deployment manager')
    @api.marshal_with(model)
    def get(self, deploymentManagerID):
        result = ocloud_view.deployment_manager_one(
            deploymentManagerID, uow)
        if result is not None:
            return result
        api.abort(404, "Deployment manager {} doesn't exist".format(
            deploymentManagerID))


# ----------  Subscriptions ---------- #
@api.route("/subscriptions")
class SubscriptionsListRouter(Resource):

    model = SubscriptionDTO.subscription_get
    expect = SubscriptionDTO.subscription
    post_resp = SubscriptionDTO.subscription_post_resp

    @api.doc('List subscriptions')
    @api.marshal_list_with(model)
    def get(self):
        return ocloud_view.subscriptions(uow)

    @api.doc('Create a subscription')
    @api.expect(expect)
    @api.marshal_with(post_resp, code=201)
    def post(self):
        data = api.payload
        sub_uuid = str(uuid.uuid4())
        subscription = Subscription(
            sub_uuid, data['callback'], data['consumerSubscriptionId'],
            data['filter'])
        ocloud_view.subscription_create(subscription, uow)
        return {"subscriptionId": sub_uuid}, 201


@api.route("/subscriptions/<subscriptionID>")
@api.param('subscriptionID', 'ID of the subscription')
@api.response(404, 'Subscription not found')
class SubscriptionGetDelRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api.doc('Get subscription by ID')
    @api.marshal_with(model)
    def get(self, subscriptionID):
        result = ocloud_view.subscription_one(
            subscriptionID, uow)
        if result is not None:
            return result
        api.abort(404, "Subscription {} doesn't exist".format(
            subscriptionID))

    @api.doc('Delete subscription by ID')
    @api.response(204, 'Subscription deleted')
    def delete(self, subscriptionID):
        with uow:
            uow.subscriptions.delete(subscriptionID)
            uow.commit()
        return '', 204


def configure_namespace(app, bus):

    api_v1 = api
    app.add_namespace(api_v1, path=apibase)

    # Set global uow
    global uow
    uow = bus.uow
