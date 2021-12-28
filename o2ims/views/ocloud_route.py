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

from flask_restx import Resource

from o2ims.views import ocloud_view, api_ims_inventory_v1
from o2common.config import config
from o2ims.views.ocloud_dto import OcloudDTO, ResourceTypeDTO,\
    ResourcePoolDTO, ResourceDTO, DeploymentManagerDTO, SubscriptionDTO,\
    ConfigurationDTO


apibase = config.get_o2ims_api_base()


# ----------  OClouds ---------- #
@api_ims_inventory_v1.route("/")
@api_ims_inventory_v1.response(404, 'oCloud not found')
class OcloudsListRouter(Resource):
    """Ocloud get endpoint
    O2 interface ocloud endpoint
    """

    ocloud_get = OcloudDTO.ocloud

    @api_ims_inventory_v1.marshal_with(ocloud_get)
    def get(self):
        res = ocloud_view.oclouds(bus.uow)
        if len(res) > 0:
            return res[0]
        api_ims_inventory_v1.abort(
            404, "oCloud doesn't exist")


# ----------  ResourceTypes ---------- #
@api_ims_inventory_v1.route("/resourceTypes")
class ResourceTypesListRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        return ocloud_view.resource_types(bus.uow)


@api_ims_inventory_v1.route("/resourceTypes/<resourceTypeID>")
@api_ims_inventory_v1.param('resourceTypeID', 'ID of the resource type')
@api_ims_inventory_v1.response(404, 'Resource type not found')
class ResourceTypeGetRouter(Resource):

    model = ResourceTypeDTO.resource_type_get

    @api_ims_inventory_v1.doc('Get resource type')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, resourceTypeID):
        result = ocloud_view.resource_type_one(resourceTypeID, bus.uow)
        if result is not None:
            return result
        api_ims_inventory_v1.abort(
            404, "Resource type {} doesn't exist".format(resourceTypeID))


# ----------  ResourcePools ---------- #
@api_ims_inventory_v1.route("/resourcePools")
class ResourcePoolsListRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        return ocloud_view.resource_pools(bus.uow)


@api_ims_inventory_v1.route("/resourcePools/<resourcePoolID>")
@api_ims_inventory_v1.param('resourcePoolID', 'ID of the resource pool')
@api_ims_inventory_v1.response(404, 'Resource pool not found')
class ResourcePoolGetRouter(Resource):

    model = ResourcePoolDTO.resource_pool_get

    @api_ims_inventory_v1.doc('Get resource pool')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, resourcePoolID):
        result = ocloud_view.resource_pool_one(resourcePoolID, bus.uow)
        if result is not None:
            return result
        api_ims_inventory_v1.abort(
            404, "Resource pool {} doesn't exist".format(resourcePoolID))


# ----------  Resources ---------- #
@api_ims_inventory_v1.route("/resourcePools/<resourcePoolID>/resources")
@api_ims_inventory_v1.param('resourcePoolID', 'ID of the resource pool')
class ResourcesListRouter(Resource):

    model = ResourceDTO.resource_list

    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self, resourcePoolID):
        return ocloud_view.resources(resourcePoolID, bus.uow)


@api_ims_inventory_v1.route(
    "/resourcePools/<resourcePoolID>/resources/<resourceID>")
@api_ims_inventory_v1.param('resourcePoolID', 'ID of the resource pool')
@api_ims_inventory_v1.param('resourceID', 'ID of the resource')
@api_ims_inventory_v1.response(404, 'Resource not found')
class ResourceGetRouter(Resource):

    # dto = ResourceDTO()
    # model = dto.get_resource_get()
    model = ResourceDTO.recursive_resource_mapping()

    @api_ims_inventory_v1.doc('Get resource')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, resourcePoolID, resourceID):
        result = ocloud_view.resource_one(resourceID, bus.uow)
        if result is not None:
            return result
        api_ims_inventory_v1.abort(
            404, "Resource {} doesn't exist".format(resourceID))


# ----------  DeploymentManagers ---------- #
@api_ims_inventory_v1.route("/deploymentManagers")
class DeploymentManagersListRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        return ocloud_view.deployment_managers(bus.uow)


@api_ims_inventory_v1.route("/deploymentManagers/<deploymentManagerID>")
@api_ims_inventory_v1.param('deploymentManagerID',
                            'ID of the deployment manager')
@api_ims_inventory_v1.response(404, 'Deployment manager not found')
class DeploymentManagerGetRouter(Resource):

    model = DeploymentManagerDTO.deployment_manager_get

    @api_ims_inventory_v1.doc('Get deployment manager')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, deploymentManagerID):
        result = ocloud_view.deployment_manager_one(
            deploymentManagerID, bus.uow)
        if result is not None:
            return result
        api_ims_inventory_v1.abort(
            404,
            "Deployment manager {} doesn't exist".format(deploymentManagerID))


# ----------  Subscriptions ---------- #
@api_ims_inventory_v1.route("/subscriptions")
class SubscriptionsListRouter(Resource):

    model = SubscriptionDTO.subscription_get
    expect = SubscriptionDTO.subscription
    post_resp = SubscriptionDTO.subscription_post_resp

    @api_ims_inventory_v1.doc('List subscriptions')
    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        return ocloud_view.subscriptions(bus.uow)

    @api_ims_inventory_v1.doc('Create a subscription')
    @api_ims_inventory_v1.expect(expect)
    @api_ims_inventory_v1.marshal_with(post_resp, code=201)
    def post(self):
        data = api_ims_inventory_v1.payload
        result = ocloud_view.subscription_create(data, bus.uow)
        return result, 201


@api_ims_inventory_v1.route("/subscriptions/<subscriptionID>")
@api_ims_inventory_v1.param('subscriptionID', 'ID of the subscription')
@api_ims_inventory_v1.response(404, 'Subscription not found')
class SubscriptionGetDelRouter(Resource):

    model = SubscriptionDTO.subscription_get

    @api_ims_inventory_v1.doc('Get subscription by ID')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, subscriptionID):
        result = ocloud_view.subscription_one(
            subscriptionID, bus.uow)
        if result is not None:
            return result
        api_ims_inventory_v1.abort(404, "Subscription {} doesn't exist".format(
            subscriptionID))

    @api_ims_inventory_v1.doc('Delete subscription by ID')
    @api_ims_inventory_v1.response(204, 'Subscription deleted')
    def delete(self, subscriptionID):
        result = ocloud_view.subscription_delete(subscriptionID, bus.uow)
        return result, 204


# ----------  Registration ---------- #
@api_ims_inventory_v1.route("/configurations")
class ConfigurationListRouter(Resource):

    model = ConfigurationDTO.configuration_get
    expect = ConfigurationDTO.configuration
    post_resp = ConfigurationDTO.configuration_post_resp

    @api_ims_inventory_v1.doc('List registrations')
    @api_ims_inventory_v1.marshal_list_with(model)
    def get(self):
        return ocloud_view.configurations(bus.uow)

    @api_ims_inventory_v1.doc('Create a registration')
    @api_ims_inventory_v1.expect(expect)
    @api_ims_inventory_v1.marshal_with(post_resp, code=201)
    def post(self):
        data = api_ims_inventory_v1.payload
        result = ocloud_view.configuration_create(data, bus)
        return result, 201


@api_ims_inventory_v1.route("/configurations/<configurationID>")
@api_ims_inventory_v1.param('configurationID', 'ID of the configuration')
@api_ims_inventory_v1.response(404, 'Configuration not found')
class ConfigurationGetDelRouter(Resource):

    model = ConfigurationDTO.configuration_get

    @api_ims_inventory_v1.doc('Get configuration by ID')
    @api_ims_inventory_v1.marshal_with(model)
    def get(self, configurationID):
        result = ocloud_view.configuration_one(
            configurationID, bus.uow)
        if result is not None:
            return result
        api_ims_inventory_v1.abort(404, "Configuration {} doesn't exist".format(
            configurationID))

    @api_ims_inventory_v1.doc('Delete configuration by ID')
    @api_ims_inventory_v1.response(204, 'Configuration deleted')
    def delete(self, configurationID):
        result = ocloud_view.configuration_delete(configurationID, bus.uow)
        return result, 204


def configure_namespace(app, bus_new):

    # Set global bus for resource
    global bus
    bus = bus_new

    app.add_namespace(api_ims_inventory_v1, path=apibase)
